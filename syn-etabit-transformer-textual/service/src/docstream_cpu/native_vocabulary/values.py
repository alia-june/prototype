"""Immutable records and approved ceilings for the AUTH-17 vocabulary pilot."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Mapping

from docstream_cpu.native import NativeError


PILOT_SCHEMA = "docstream.native-vocabulary.pilot/1"
FORM_SCHEMA = "docstream.native-vocabulary.form/1"
EXCEPTION_SCHEMA = "docstream.native-vocabulary.exception/1"
FRAGMENT_SCHEMA = "docstream.native-vocabulary.fragment/1"
CONSTRUCTION_SCHEMA = "docstream.native-vocabulary.construction/1"
SOURCE_NAME = "Princeton WordNet 3.1 database-only"
SOURCE_SHA256 = "3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a"
POS_ORDER = ("noun", "verb", "adj", "adv")
MAX_APPROVED_FORMS = 1_000
MAX_APPROVED_EXCEPTIONS = 100
MAX_APPROVED_SOURCE_BYTES = 8 * 1024 * 1024
MAX_APPROVED_SOURCE_RECORDS = 10_000
MAX_APPROVED_SECONDS = 600.0
MAX_APPROVED_MEMORY_BYTES = 512 * 1024 * 1024


class VocabularyError(NativeError):
    """A structured pilot error; ``code`` is inherited from NativeError."""


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise VocabularyError(code, message)


def exact_integer(value: object, label: str, minimum: int, maximum: int) -> None:
    require(type(value) is int and minimum <= value <= maximum, "VALIDATION_ERROR",
            f"{label} requires an exact integer in [{minimum}, {maximum}]")


@dataclass(frozen=True, slots=True)
class PilotLimits:
    forms_per_pos: int = 250
    exception_pairs_per_pos: int = 25
    max_source_bytes: int = MAX_APPROVED_SOURCE_BYTES
    max_source_records: int = MAX_APPROVED_SOURCE_RECORDS

    def __post_init__(self):
        exact_integer(self.forms_per_pos, "forms_per_pos", 1, MAX_APPROVED_FORMS // 4)
        exact_integer(self.exception_pairs_per_pos, "exception_pairs_per_pos", 0,
                      MAX_APPROVED_EXCEPTIONS // 4)
        exact_integer(self.max_source_bytes, "max_source_bytes", 1, MAX_APPROVED_SOURCE_BYTES)
        exact_integer(self.max_source_records, "max_source_records", 1,
                      MAX_APPROVED_SOURCE_RECORDS)

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceLocator:
    member: str
    line: int
    byte_offset: int
    line_sha256: str

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class FormRecord:
    part_of_speech: str
    synset_offset: str
    synset_type: str
    word_position: int
    raw_token: str
    form: str
    lex_id: str
    syntactic_marker: str | None
    locator: SourceLocator
    definition_id: str = ""
    construction_id: str = ""

    def to_record(self) -> dict:
        result = asdict(self)
        result["schema"] = FORM_SCHEMA
        return result


@dataclass(frozen=True, slots=True)
class ExceptionRecord:
    part_of_speech: str
    inflected: str
    base: str
    base_position: int
    locator: SourceLocator
    inflected_definition_id: str = ""
    base_definition_id: str = ""

    def to_record(self) -> dict:
        result = asdict(self)
        result["schema"] = EXCEPTION_SCHEMA
        return result


@dataclass(frozen=True, slots=True)
class FragmentRecord:
    fragment_id: str
    text: str
    layer: str
    definition_id: str
    child_fragment_ids: tuple[str, ...]
    literal_symbol_values: tuple[int, ...]
    selectable: bool = True

    def to_record(self) -> dict:
        result = asdict(self)
        result["schema"] = FRAGMENT_SCHEMA
        return result


@dataclass(frozen=True, slots=True)
class ConstructionPiece:
    kind: str
    start: int
    end: int
    text: str
    fragment_id: str | None = None
    symbol_value: int | None = None

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConstructionRecord:
    text: str
    definition_id: str
    pieces: tuple[ConstructionPiece, ...]

    def to_record(self) -> dict:
        return {"schema": CONSTRUCTION_SCHEMA, "text": self.text,
                "definition_id": self.definition_id,
                "pieces": [piece.to_record() for piece in self.pieces]}


@dataclass(frozen=True, slots=True)
class PilotResult:
    status: str
    source_sha256: str
    limits: PilotLimits
    source_bytes_read: int
    source_records_read: int
    forms: tuple[FormRecord, ...]
    exceptions: tuple[ExceptionRecord, ...]
    fragments: tuple[FragmentRecord, ...]
    constructions: tuple[ConstructionRecord, ...]
    shortages: Mapping[str, int]
    excluded_collocations: int
    model_stats: Mapping[str, object]

    def __post_init__(self):
        require(self.status in ("COMPLETE", "PARTIAL"), "INVARIANT_ERROR",
                "pilot status must be COMPLETE or PARTIAL")
        require(type(self.shortages) is MappingProxyType, "INVARIANT_ERROR",
                "shortages must be an immutable mapping")
        require(type(self.model_stats) is MappingProxyType, "INVARIANT_ERROR",
                "model_stats must be an immutable mapping")

    def to_summary(self) -> dict:
        by_pos = {pos: sum(record.part_of_speech == pos for record in self.forms)
                  for pos in POS_ORDER}
        exception_by_pos = {
            pos: sum(record.part_of_speech == pos for record in self.exceptions)
            for pos in POS_ORDER
        }
        return {
            "schema": PILOT_SCHEMA,
            "status": self.status,
            "source": SOURCE_NAME,
            "source_sha256": self.source_sha256,
            "limits": self.limits.to_record(),
            "source_bytes_read": self.source_bytes_read,
            "source_records_read": self.source_records_read,
            "form_records": len(self.forms),
            "form_records_by_pos": by_pos,
            "exception_pairs": len(self.exceptions),
            "exception_pairs_by_pos": exception_by_pos,
            "fragment_definitions": len(self.fragments),
            "unique_word_constructions": len(self.constructions),
            "shortages": dict(self.shortages),
            "excluded_collocations": self.excluded_collocations,
            "model_stats": dict(self.model_stats),
        }
