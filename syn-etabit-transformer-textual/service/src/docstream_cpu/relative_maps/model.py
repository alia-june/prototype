"""Atomic in-memory catalog for relative, immutable and replaceable map definitions."""
from __future__ import annotations

from dataclasses import dataclass, replace
from threading import RLock
from types import MappingProxyType
from typing import Mapping

from .values import (MapDefinition, MapDraft, MapEntry, MapError, MapLimits, MapRef,
                     digest_id, require)


@dataclass(frozen=True, slots=True)
class _State:
    definitions: Mapping[str, MapDefinition]
    publications: int = 0


def _frozen(source):
    return MappingProxyType(dict(source))


class RelativeMapStore:
    def __init__(self, limits: MapLimits | None = None):
        require(limits is None or type(limits) is MapLimits, "VALIDATION_ERROR",
                "limits must be exact MapLimits")
        self._limits = limits if limits is not None else MapLimits()
        self._state = _State(_frozen({}))
        self._lock = RLock()

    @property
    def limits(self) -> MapLimits:
        return self._limits

    @property
    def definitions(self) -> Mapping[str, MapDefinition]:
        with self._lock:
            return self._state.definitions

    def stats(self) -> dict:
        with self._lock:
            return {"maps": len(self._state.definitions),
                    "entries": sum(len(item.entries) for item in self._state.definitions.values()),
                    "publications": self._state.publications}

    def definition(self, ref: MapRef) -> MapDefinition:
        require(type(ref) is MapRef, "VALIDATION_ERROR", "definition requires exact MapRef")
        try:
            return self._state.definitions[ref.map_id]
        except KeyError as exc:
            raise MapError("UNKNOWN_MAP", "map is not in this store") from exc

    def publish_batch(self, drafts: tuple[MapDraft, ...]) -> Mapping[str, MapRef]:
        """Resolve local dependencies and publish the entire acyclic batch once."""
        with self._lock:
            require(type(drafts) is tuple, "VALIDATION_ERROR", "drafts must be immutable tuple")
            require(0 < len(drafts) <= self._limits.max_batch, "LIMIT_EXCEEDED",
                    "batch size is outside store limits")
            for draft in drafts:
                require(type(draft) is MapDraft, "VALIDATION_ERROR", "batch requires exact MapDraft values")
                draft.__post_init__()
                require(len(draft.entries) <= self._limits.max_entries, "LIMIT_EXCEEDED",
                        "map entry limit exceeded")
                require(len(draft.input_keys) <= self._limits.max_inputs, "LIMIT_EXCEEDED",
                        "map input limit exceeded")
            by_key = {draft.key: draft for draft in drafts}
            require(len(by_key) == len(drafts), "DUPLICATE_DRAFT_KEY", "draft keys must be unique")
            existing = dict(self._state.definitions)
            for draft in drafts:
                for input_key in draft.input_keys:
                    if input_key in by_key:
                        continue
                    try:
                        digest_id(input_key, "external input key")
                    except MapError as exc:
                        raise MapError("UNKNOWN_INPUT", "input is neither a local draft nor a map ID") from exc
                    require(input_key in existing, "UNKNOWN_INPUT", "external input map is absent")

            pending = dict(by_key)
            resolved: dict[str, MapRef] = {}
            staged = dict(existing)
            while pending:
                progress = False
                for key, draft in tuple(pending.items()):
                    if any(value in pending for value in draft.input_keys):
                        continue
                    inputs = tuple(resolved[value].map_id if value in resolved else value
                                   for value in draft.input_keys)
                    candidate = MapDefinition(draft.map_type, draft.name, draft.version,
                                              draft.context_id, inputs, draft.entries)
                    self._validate_candidate(candidate)
                    if candidate.map_id in staged:
                        require(staged[candidate.map_id] == candidate, "INVARIANT_ERROR",
                                "map digest collision")
                    else:
                        require(len(staged) < self._limits.max_maps, "LIMIT_EXCEEDED",
                                "map count limit exceeded")
                        staged[candidate.map_id] = candidate
                    resolved[key] = MapRef(candidate.map_id)
                    del pending[key]
                    progress = True
                if not progress:
                    raise MapError("DEPENDENCY_CYCLE", "local map dependencies contain a cycle")
            next_state = _State(_frozen(staged), self._state.publications + 1)
            self._state = next_state
            return MappingProxyType(dict(resolved))

    @staticmethod
    def _validate_candidate(candidate: MapDefinition) -> None:
        """Validate generic map mechanics without inventing domain semantics."""
        if candidate.map_type == "orders":
            for entry in candidate.entries:
                require(entry.entry_kind == "order", "INVALID_ORDER",
                        "order maps may contain only explicit order entries")
                payload = entry.payload
                sequences = [payload.get(name) for name in ("object_ids", "relation_ids")
                             if name in payload]
                require(len(sequences) == 1 and type(sequences[0]) is list,
                        "INVALID_ORDER", "order requires exactly one ID sequence")
                values = sequences[0]
                require(all(type(value) is str for value in values), "INVALID_ORDER",
                        "order IDs must be exact strings")
                positions = payload.get("positions")
                require(type(positions) is list and positions == list(range(len(values))),
                        "INVALID_ORDER", "order positions must be exact contiguous indices")
        if candidate.map_type == "context":
            selections = [entry for entry in candidate.entries if entry.entry_kind == "selection"]
            require(bool(selections), "INVALID_SELECTION", "context requires a selection")
            for entry in selections:
                payload = entry.payload
                index = payload.get("selected_input_index")
                require(type(index) is int and not isinstance(index, bool)
                        and 0 <= index < len(candidate.input_map_ids), "INVALID_SELECTION",
                        "context selection index is outside inputs")
        if candidate.map_type == "replacement-ledger":
            for entry in candidate.entries:
                if entry.entry_kind != "replacement":
                    continue
                payload = entry.payload
                for name in ("prior_input_index", "replacement_input_index"):
                    index = payload.get(name)
                    require(type(index) is int and not isinstance(index, bool)
                            and 0 <= index < len(candidate.input_map_ids), "INVALID_REPLACEMENT",
                            "replacement index is outside inputs")

    def resolve_role(self, context: MapRef, role: str) -> MapRef:
        """Resolve a role from one immutable context map; no global active head exists."""
        require(type(context) is MapRef, "VALIDATION_ERROR", "context requires exact MapRef")
        require(type(role) is str, "VALIDATION_ERROR", "role must be exact str")
        definition = self.definition(context)
        require(definition.map_type == "context", "MAP_TYPE_MISMATCH", "map is not a context")
        matches = []
        for entry in definition.entries:
            if entry.entry_kind != "selection":
                continue
            payload = entry.payload
            if payload.get("role") != role:
                continue
            index = payload.get("selected_input_index")
            require(type(index) is int and not isinstance(index, bool), "INVALID_SELECTION",
                    "selection index must be an exact integer")
            require(0 <= index < len(definition.input_map_ids), "INVALID_SELECTION",
                    "selection index is outside context inputs")
            matches.append(definition.input_map_ids[index])
        require(len(matches) == 1, "INVALID_SELECTION", "context must have exactly one role selection")
        require(matches[0] in self._state.definitions, "UNKNOWN_MAP", "selected map is absent")
        return MapRef(matches[0])

    def lineage(self, ref: MapRef) -> tuple[MapRef, ...]:
        """Return all reachable map identities once, including the requested map."""
        with self._lock:
            self.definition(ref)
            pending, seen, output = [ref.map_id], set(), []
            while pending:
                current = pending.pop()
                if current in seen:
                    continue
                seen.add(current)
                output.append(MapRef(current))
                pending.extend(reversed(self._state.definitions[current].input_map_ids))
            return tuple(output)
