"""Strict, immutable values for the native ASCII test profile; no lexical inference."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from hashlib import sha256
import json
import re


PROFILE = "docstream.native.safe-ascii/1"
ASSEMBLY_SCHEMA = "docstream.native.assembly/1"
MAX_CHILDREN = 10_000
MAX_PATH = 8


class NativeError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def require(condition: bool, message: str, code: str = "VALIDATION_ERROR") -> None:
    if not condition:
        raise NativeError(code, message)


def exact_integer(value: object, label: str, minimum: int, maximum: int) -> None:
    require(type(value) is int and minimum <= value <= maximum,
            f"{label} requires an exact integer in [{minimum}, {maximum}]")


def identifier(value: object, label: str) -> None:
    require(type(value) is str and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value) is not None,
            f"{label} requires 1..128 ASCII identifier characters")


def sealed_id(value: object) -> None:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            "definition ID requires a lower-case SHA-256 digest")


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


class Layer(IntEnum):
    GLYPH = 1
    COMPONENT = 2
    ROOT = 3
    WORD = 4
    PHRASE = 5
    SENTENCE = 6
    PARAGRAPH = 7
    DOCUMENT = 8


@dataclass(frozen=True, slots=True)
class SymbolRef:
    value: int

    def __post_init__(self):
        exact_integer(self.value, "symbol", 0, 127)


@dataclass(frozen=True, slots=True)
class AssemblyRef:
    definition_id: str

    def __post_init__(self):
        sealed_id(self.definition_id)


Reference = SymbolRef | AssemblyRef


def check_reference(value: object) -> None:
    require(type(value) in (SymbolRef, AssemblyRef), "expected a native symbol or assembly reference")
    # Validate at the boundary as well as construction; do not trust subclass coercions.
    value.__post_init__()


def reference_record(ref: Reference) -> dict:
    check_reference(ref)
    if type(ref) is SymbolRef:
        return {"kind": "symbol", "value": ref.value}
    return {"kind": "assembly", "definition_id": ref.definition_id}


def check_children(children: object) -> None:
    require(type(children) is tuple, "children must be an immutable tuple")
    require(len(children) <= MAX_CHILDREN, "too many direct children", "LIMIT_EXCEEDED")
    for child in children:
        check_reference(child)


def ascii_symbols(value: str | bytes) -> tuple[SymbolRef, ...]:
    """Literal conversion only: preserve controls, case, punctuation and spacing."""
    require(type(value) in (str, bytes), "literal input must be exact str or bytes")
    require(len(value) <= MAX_CHILDREN, "literal input too long", "LIMIT_EXCEEDED")
    if type(value) is str:
        try:
            value = value.encode("ascii", errors="strict")
        except UnicodeError as exc:
            raise NativeError("VALIDATION_ERROR", "safe mode accepts only ASCII positions 0..127") from exc
    require(all(n < 128 for n in value), "safe mode accepts only ASCII positions 0..127")
    return tuple(SymbolRef(n) for n in value)


@dataclass(frozen=True, slots=True)
class Alphabet:
    profile: str = field(default=PROFILE, init=False)
    symbols: tuple[SymbolRef, ...] = field(
        default_factory=lambda: tuple(SymbolRef(n) for n in range(128)), init=False)


@dataclass(frozen=True, slots=True)
class Assembly:
    layer: Layer
    children: tuple[Reference, ...]
    definition_id: str = field(init=False)

    def __post_init__(self):
        require(type(self.layer) is Layer, "layer must be an explicit Layer member")
        check_children(self.children)
        object.__setattr__(self, "definition_id", sha256(canonical(self.to_record())).hexdigest())

    def to_record(self) -> dict:
        return {"schema_version": ASSEMBLY_SCHEMA, "profile": PROFILE,
                "layer": self.layer.name.lower(),
                "children": [reference_record(ref) for ref in self.children]}

    @property
    def ref(self) -> AssemblyRef:
        return AssemblyRef(self.definition_id)


@dataclass(frozen=True, slots=True)
class Edit:
    operation_id: str
    kind: str
    path: tuple[int, ...] = ()
    index: int = 0
    count: int = 0
    references: tuple[Reference, ...] = ()

    def __post_init__(self):
        identifier(self.operation_id, "operation_id")
        require(type(self.kind) is str and self.kind in ("insert", "remove", "replace"),
                "unknown native edit kind")
        require(type(self.path) is tuple and len(self.path) <= MAX_PATH,
                "path must be an immutable tuple of at most eight child indices")
        for index in self.path:
            exact_integer(index, "path index", 0, MAX_CHILDREN - 1)
        exact_integer(self.index, "edit index", 0, MAX_CHILDREN)
        exact_integer(self.count, "edit count", 0, MAX_CHILDREN)
        check_children(self.references)
        if self.kind == "insert":
            require(self.count == 0 and bool(self.references), "insert requires count=0 and references")
        elif self.kind == "remove":
            require(self.count > 0 and not self.references, "remove requires positive count and no references")
        else:
            require(self.count > 0 and bool(self.references), "replace requires positive count and references")

    def to_record(self) -> dict:
        return {"operation_id": self.operation_id, "kind": self.kind, "path": list(self.path),
                "index": self.index, "count": self.count,
                "references": [reference_record(ref) for ref in self.references]}


@dataclass(frozen=True, slots=True)
class Limits:
    max_definitions: int = 4096
    max_total_references: int = 5_100_000
    max_children: int = MAX_CHILDREN
    max_expanded_bytes: int = 1_000_000
    max_expansion_steps: int = 2_000_000
    max_streams: int = 4096
    max_batches: int = 2048
    max_operations: int = 256

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            exact_integer(getattr(self, name), name, 1, 10_000_000)
        require(self.max_children <= MAX_CHILDREN, "max_children cannot exceed the profile ceiling")
        require(self.max_operations <= 256, "max_operations cannot exceed 256")


@dataclass(frozen=True, slots=True)
class Stream:
    stream_id: str
    root: AssemblyRef
    parent_id: str | None
    batch_id: str | None
    operation_id: str | None


@dataclass(frozen=True, slots=True)
class BatchResult:
    batch_id: str
    base_stream_id: str
    operations: tuple[Edit, ...]
    output_stream_ids: tuple[str, ...]
    request_sha256: str

    @property
    def result_stream_id(self) -> str:
        return self.output_stream_ids[-1]


@dataclass(frozen=True, slots=True)
class Inspection:
    stream_id: str
    path: tuple[int, ...]
    reference: Reference
    layer: Layer | None
    expanded_bytes: int
