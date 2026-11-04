"""Strict immutable values for AUTH-18A relative and replaceable maps."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import re


MAP_SCHEMA = "docstream.relative-map/1"
ENTRY_SCHEMA = "docstream.relative-map.entry/1"
PROFILE = "docstream.relative-maps.auth18a/1"
MAP_TYPES = frozenset({"objects", "orders", "structures", "processes", "grammar",
                       "syntax", "theory", "relations", "composed", "context",
                       "replacement-ledger", "derivation-ledger"})
MAX_ENTRIES = 100_000


class MapError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise MapError(code, message)


def identifier(value: object, label: str) -> None:
    require(type(value) is str and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value) is not None,
            "VALIDATION_ERROR", f"{label} requires 1..128 identifier characters")


def digest_id(value: object, label: str = "map_id") -> None:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            "VALIDATION_ERROR", f"{label} requires a lower-case SHA-256 digest")


def exact_integer(value: object, label: str, minimum: int, maximum: int) -> None:
    require(type(value) is int and minimum <= value <= maximum, "VALIDATION_ERROR",
            f"{label} requires an exact integer in [{minimum}, {maximum}]")


def canonical(value: object) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=True, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise MapError("VALIDATION_ERROR", "value is not canonical JSON data") from exc


@dataclass(frozen=True, slots=True)
class MapEntry:
    entry_kind: str
    payload_json: str
    entry_id: str = field(init=False)

    def __post_init__(self):
        identifier(self.entry_kind, "entry_kind")
        require(type(self.payload_json) is str, "VALIDATION_ERROR", "payload_json must be exact str")
        try:
            value = json.loads(self.payload_json)
        except json.JSONDecodeError as exc:
            raise MapError("VALIDATION_ERROR", "payload_json is invalid JSON") from exc
        require(type(value) is dict, "VALIDATION_ERROR", "entry payload must be an object")
        normalized = canonical(value).decode("ascii")
        require(normalized == self.payload_json, "NON_CANONICAL_ENTRY",
                "entry payload must use canonical JSON encoding")
        object.__setattr__(self, "entry_id", sha256(canonical(self.to_record())).hexdigest())

    @classmethod
    def create(cls, entry_kind: str, payload: dict) -> "MapEntry":
        require(type(payload) is dict, "VALIDATION_ERROR", "entry payload must be an exact dict")
        return cls(entry_kind, canonical(payload).decode("ascii"))

    @property
    def payload(self) -> dict:
        return json.loads(self.payload_json)

    def to_record(self) -> dict:
        return {"schema": ENTRY_SCHEMA, "entry_kind": self.entry_kind,
                "payload": self.payload}


@dataclass(frozen=True, slots=True)
class MapDraft:
    key: str
    map_type: str
    name: str
    version: int
    context_id: str
    input_keys: tuple[str, ...] = ()
    entries: tuple[MapEntry, ...] = ()

    def __post_init__(self):
        identifier(self.key, "draft key")
        require(re.fullmatch(r"[0-9a-f]{64}", self.key) is None, "VALIDATION_ERROR",
                "draft key cannot be confused with a map digest")
        require(type(self.map_type) is str and self.map_type in MAP_TYPES,
                "VALIDATION_ERROR", "unknown map type")
        identifier(self.name, "map name")
        exact_integer(self.version, "map version", 1, 1_000_000)
        identifier(self.context_id, "context_id")
        require(type(self.input_keys) is tuple and len(self.input_keys) <= 256,
                "VALIDATION_ERROR", "input_keys must be an immutable tuple of at most 256 values")
        for value in self.input_keys:
            identifier(value, "input key")
        require(type(self.entries) is tuple and len(self.entries) <= MAX_ENTRIES,
                "VALIDATION_ERROR", "entries must be an immutable bounded tuple")
        for value in self.entries:
            require(type(value) is MapEntry, "VALIDATION_ERROR", "entries require exact MapEntry values")
            value.__post_init__()


@dataclass(frozen=True, slots=True)
class MapDefinition:
    map_type: str
    name: str
    version: int
    context_id: str
    input_map_ids: tuple[str, ...]
    entries: tuple[MapEntry, ...]
    map_id: str = field(init=False)

    def __post_init__(self):
        require(self.map_type in MAP_TYPES, "INVARIANT_ERROR", "unknown stored map type")
        identifier(self.name, "map name")
        exact_integer(self.version, "map version", 1, 1_000_000)
        identifier(self.context_id, "context_id")
        require(type(self.input_map_ids) is tuple, "INVARIANT_ERROR", "stored inputs must be tuple")
        for value in self.input_map_ids:
            digest_id(value, "input map ID")
        require(type(self.entries) is tuple, "INVARIANT_ERROR", "stored entries must be tuple")
        object.__setattr__(self, "map_id", sha256(canonical(self.to_record())).hexdigest())

    def to_record(self) -> dict:
        return {"schema": MAP_SCHEMA, "profile": PROFILE, "map_type": self.map_type,
                "name": self.name, "version": self.version, "context_id": self.context_id,
                "input_map_ids": list(self.input_map_ids),
                "entries": [entry.to_record() for entry in self.entries]}


@dataclass(frozen=True, slots=True)
class MapRef:
    map_id: str

    def __post_init__(self):
        digest_id(self.map_id)


@dataclass(frozen=True, slots=True)
class MapLimits:
    max_maps: int = 2048
    max_entries: int = MAX_ENTRIES
    max_batch: int = 128
    max_inputs: int = 256

    def __post_init__(self):
        exact_integer(self.max_maps, "max_maps", 1, 100_000)
        exact_integer(self.max_entries, "max_entries", 1, MAX_ENTRIES)
        exact_integer(self.max_batch, "max_batch", 1, 1024)
        exact_integer(self.max_inputs, "max_inputs", 1, 256)
