"""Owned, in-memory native catalog. Batch publication replaces one state pointer."""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from threading import RLock
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4

from .values import (Alphabet, Assembly, AssemblyRef, BatchResult, Edit, Inspection,
                     Layer, Limits, MAX_PATH, NativeError, PROFILE, Reference,
                     Stream, SymbolRef, canonical, check_reference, exact_integer,
                     identifier, require)


@dataclass(frozen=True, slots=True)
class _State:
    definitions: Mapping[str, Assembly]
    lengths: Mapping[str, int]
    costs: Mapping[str, int]
    streams: Mapping[str, Stream]
    batches: Mapping[str, BatchResult]
    reference_slots: int = 0
    next_stream: int = 1
    next_batch: int = 1


def frozen_map(source):
    return MappingProxyType(dict(source))


class NativeModel:
    """No parser, meaning inference, executable hooks, database or rendering backend.

    Instances own their catalog. All public operations hold the instance lock;
    Python object access is not a security boundary against hostile caller code.
    """

    def __init__(self, limits: Limits | None = None):
        require(limits is None or type(limits) is Limits, "limits must be Limits")
        self._limits = limits if limits is not None else Limits()
        self._alphabet = Alphabet()
        self._namespace = uuid4().hex
        self._lock = RLock()
        self._state = _State(*(frozen_map({}) for _ in range(5)))

    @property
    def alphabet(self) -> Alphabet:
        return self._alphabet

    @property
    def limits(self) -> Limits:
        return self._limits

    @property
    def definitions(self) -> Mapping[str, Assembly]:
        with self._lock:
            return self._state.definitions

    def stats(self) -> dict:
        with self._lock:
            s = self._state
            return {"profile": PROFILE, "symbols": 128, "definitions": len(s.definitions),
                    "reference_slots": s.reference_slots, "streams": len(s.streams),
                    "batches": len(s.batches)}

    def definition(self, ref: AssemblyRef) -> Assembly:
        with self._lock:
            require(type(ref) is AssemblyRef, "definition requires AssemblyRef")
            return self._lookup(ref, self._state.definitions)

    @staticmethod
    def _lookup(ref: AssemblyRef, definitions: Mapping[str, Assembly]) -> Assembly:
        check_reference(ref)
        try:
            return definitions[ref.definition_id]
        except KeyError as exc:
            raise NativeError("UNKNOWN_REFERENCE", "assembly definition is not in this catalog") from exc

    def _stage_definition(self, layer, children, definitions, lengths, costs, slots):
        candidate = Assembly(layer, children)
        require(len(children) <= self._limits.max_children, "direct child limit exceeded", "LIMIT_EXCEEDED")
        expanded = 0
        steps = 1
        for ref in children:
            if type(ref) is SymbolRef:
                expanded += 1
                steps += 1
            else:
                child = self._lookup(ref, definitions)
                require(child.layer < layer, "assemblies may reference only lower layers", "LAYER_MISMATCH")
                expanded += lengths[ref.definition_id]
                steps += costs[ref.definition_id]
            require(expanded <= self._limits.max_expanded_bytes,
                    "expanded byte limit exceeded", "LIMIT_EXCEEDED")
            require(steps <= self._limits.max_expansion_steps,
                    "expansion traversal limit exceeded", "LIMIT_EXCEEDED")
        key = candidate.definition_id
        if key in definitions:
            require(definitions[key] == candidate, "definition digest collision", "INVARIANT_ERROR")
            return candidate.ref, slots
        require(len(definitions) < self._limits.max_definitions, "definition limit exceeded", "LIMIT_EXCEEDED")
        require(slots + len(children) <= self._limits.max_total_references,
                "total reference limit exceeded", "LIMIT_EXCEEDED")
        definitions[key] = candidate
        lengths[key] = expanded
        costs[key] = steps
        return candidate.ref, slots + len(children)

    def define(self, layer: Layer, children: tuple[Reference, ...]) -> AssemblyRef:
        """Explicit structural construction; identical definitions share identity."""
        with self._lock:
            s = self._state
            definitions, lengths, costs = dict(s.definitions), dict(s.lengths), dict(s.costs)
            ref, slots = self._stage_definition(layer, children, definitions, lengths, costs, s.reference_slots)
            self._state = replace(s, definitions=frozen_map(definitions), lengths=frozen_map(lengths),
                                  costs=frozen_map(costs), reference_slots=slots)
            return ref

    def _stream_id(self, ordinal: int) -> str:
        return f"native:{self._namespace}:stream:{ordinal}"

    def _batch_id(self, ordinal: int) -> str:
        return f"native:{self._namespace}:batch:{ordinal}"

    def create_stream(self, root: AssemblyRef) -> Stream:
        with self._lock:
            require(type(root) is AssemblyRef, "stream root requires AssemblyRef")
            s = self._state
            self._lookup(root, s.definitions)
            require(len(s.streams) < self._limits.max_streams, "stream limit exceeded", "LIMIT_EXCEEDED")
            stream = Stream(self._stream_id(s.next_stream), root, None, None, None)
            streams = dict(s.streams)
            streams[stream.stream_id] = stream
            self._state = replace(s, streams=frozen_map(streams), next_stream=s.next_stream + 1)
            return stream

    def stream(self, stream_id: str) -> Stream:
        with self._lock:
            identifier(stream_id, "stream_id")
            try:
                return self._state.streams[stream_id]
            except KeyError as exc:
                raise NativeError("UNKNOWN_STREAM", "stream is not in this catalog") from exc

    def batch(self, batch_id: str) -> BatchResult:
        with self._lock:
            identifier(batch_id, "batch_id")
            try:
                return self._state.batches[batch_id]
            except KeyError as exc:
                raise NativeError("UNKNOWN_BATCH", "batch is not in this catalog") from exc

    @staticmethod
    def _path(path):
        require(type(path) is tuple and len(path) <= MAX_PATH, "invalid occurrence path", "INVALID_PATH")
        for index in path:
            exact_integer(index, "path index", 0, 9999)

    def _resolve(self, root, path, definitions):
        self._path(path)
        current = root
        trail = []
        for index in path:
            require(type(current) is AssemblyRef, "path descends through a symbol", "INVALID_PATH")
            definition = self._lookup(current, definitions)
            require(index < len(definition.children), "path index outside children", "INVALID_PATH")
            trail.append((definition, index))
            current = definition.children[index]
        return current, trail

    def inspect(self, stream_id: str, path: tuple[int, ...] = ()) -> Inspection:
        with self._lock:
            stream = self.stream(stream_id)
            ref, _ = self._resolve(stream.root, path, self._state.definitions)
            layer = None if type(ref) is SymbolRef else self._state.definitions[ref.definition_id].layer
            length = 1 if type(ref) is SymbolRef else self._state.lengths[ref.definition_id]
            return Inspection(stream_id, path, ref, layer, length)

    def expand(self, ref: Reference) -> bytes:
        """Expand exact ASCII bytes without trimming or interpreting control values."""
        with self._lock:
            check_reference(ref)
            s = self._state
            if type(ref) is SymbolRef:
                return bytes((ref.value,))
            self._lookup(ref, s.definitions)
            expected = s.lengths[ref.definition_id]
            pending = [ref]
            output = bytearray()
            while pending:
                current = pending.pop()
                if type(current) is SymbolRef:
                    output.append(current.value)
                else:
                    pending.extend(reversed(s.definitions[current.definition_id].children))
            require(len(output) == expected, "stored length disagrees with expansion", "INVARIANT_ERROR")
            return bytes(output)

    def expand_stream(self, stream_id: str) -> bytes:
        with self._lock:
            return self.expand(self.stream(stream_id).root)

    def escaped(self, stream_id: str) -> str:
        """Inspection text includes quotes and escapes; never emits raw controls."""
        return ascii(self.expand_stream(stream_id).decode("ascii"))

    def history(self, stream_id: str) -> tuple[Stream, ...]:
        with self._lock:
            current = self.stream(stream_id)
            records = [current]
            while current.parent_id is not None:
                current = self._state.streams[current.parent_id]
                records.append(current)
            return tuple(reversed(records))

    def _edit(self, root, edit, definitions, lengths, costs, slots):
        target, trail = self._resolve(root, edit.path, definitions)
        require(type(target) is AssemblyRef, "edit path must select an assembly", "INVALID_PATH")
        definition = self._lookup(target, definitions)
        require(edit.index <= len(definition.children) and edit.count <= len(definition.children) - edit.index,
                "edit range outside selected assembly", "INVALID_RANGE")
        children = (definition.children[:edit.index] + edit.references
                    + definition.children[edit.index + edit.count:])
        updated, slots = self._stage_definition(definition.layer, children, definitions, lengths, costs, slots)
        # Copy only the selected occurrence's ancestry; other placements retain old references.
        for parent, index in reversed(trail):
            children = parent.children[:index] + (updated,) + parent.children[index + 1:]
            updated, slots = self._stage_definition(parent.layer, children, definitions, lengths, costs, slots)
        return updated, slots

    def apply_batch(self, base_stream_id: str, operations: tuple[Edit, ...]) -> BatchResult:
        """Stage every prefix, then publish definitions, streams and the request together.

        The library has no implicit head or external commit. Each result is an
        in-memory branch; publishing it here does not commit an existing service document.
        """
        with self._lock:
            base = self.stream(base_stream_id)
            require(type(operations) is tuple, "operations must be an immutable tuple")
            require(len(operations) <= self._limits.max_operations, "operation limit exceeded", "LIMIT_EXCEEDED")
            seen = set()
            for edit in operations:
                require(type(edit) is Edit, "operations require exact Edit values")
                edit.__post_init__()
                require(edit.operation_id not in seen, "duplicate operation ID in batch", "DUPLICATE_OPERATION")
                seen.add(edit.operation_id)
            request_hash = sha256(canonical({"schema_version": "docstream.native.batch/1", "profile": PROFILE,
                "base_stream_id": base_stream_id, "operations": [op.to_record() for op in operations]})).hexdigest()
            s = self._state
            require(len(s.batches) < self._limits.max_batches, "batch limit exceeded", "LIMIT_EXCEEDED")
            needed = max(1, len(operations))
            require(len(s.streams) + needed <= self._limits.max_streams, "stream limit exceeded", "LIMIT_EXCEEDED")
            definitions, lengths, costs = dict(s.definitions), dict(s.lengths), dict(s.costs)
            streams, batches = dict(s.streams), dict(s.batches)
            slots, ordinal = s.reference_slots, s.next_stream
            batch_id = self._batch_id(s.next_batch)
            current = base
            outputs = []
            for edit in operations:
                root, slots = self._edit(current.root, edit, definitions, lengths, costs, slots)
                current = Stream(self._stream_id(ordinal), root, current.stream_id, batch_id, edit.operation_id)
                streams[current.stream_id] = current
                outputs.append(current.stream_id)
                ordinal += 1
            if not operations:
                current = Stream(self._stream_id(ordinal), base.root, base.stream_id, batch_id, None)
                streams[current.stream_id] = current
                outputs.append(current.stream_id)
                ordinal += 1
            result = BatchResult(batch_id, base_stream_id, operations, tuple(outputs), request_hash)
            batches[batch_id] = result
            # Construct every immutable view before the one publication assignment.
            next_state = _State(frozen_map(definitions), frozen_map(lengths), frozen_map(costs), frozen_map(streams),
                                frozen_map(batches), slots, ordinal, s.next_batch + 1)
            self._state = next_state
            return result
