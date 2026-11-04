"""Bounded WordNet 3.1 intake into the safe-ASCII native CPU reference model.

This module reads exact named tar members without extracting them. WordNet
fields remain provenance. Only ordered references enter native definitions.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
import tarfile
import re

from docstream_cpu.native import Layer, NativeModel, SymbolRef, ascii_symbols

from .values import (ConstructionPiece, ConstructionRecord, ExceptionRecord,
                     FormRecord, FragmentRecord, POS_ORDER, PilotLimits,
                     PilotResult, SOURCE_SHA256, SourceLocator, VocabularyError,
                     require)


DATA_MEMBERS = {pos: f"dict/data.{pos}" for pos in POS_ORDER}
EXCEPTION_MEMBERS = {pos: f"dict/{pos}.exc" for pos in POS_ORDER}
EXPECTED_TYPES = {"noun": {"n"}, "verb": {"v"}, "adj": {"a", "s"}, "adv": {"r"}}
MAX_SOURCE_LINE_BYTES = 1_048_576
MARKERS = ("(ip)", "(p)", "(a)")


class _Budget:
    def __init__(self, limits: PilotLimits):
        self.limits = limits
        self.bytes_read = 0
        self.records_read = 0
        self.exhausted = False

    def lines(self, handle):
        line_number, byte_offset = 0, 0
        while not self.exhausted:
            remaining = self.limits.max_source_bytes - self.bytes_read
            if remaining <= 0:
                self.exhausted = True
                return
            line = handle.readline(min(remaining, MAX_SOURCE_LINE_BYTES + 1))
            if not line:
                return
            line_number += 1
            start = byte_offset
            byte_offset += len(line)
            self.bytes_read += len(line)
            if len(line) > MAX_SOURCE_LINE_BYTES:
                raise VocabularyError("SOURCE_LINE_LIMIT", "source line exceeds the one MiB pilot limit")
            if not line.endswith(b"\n") and self.bytes_read == self.limits.max_source_bytes:
                self.exhausted = True
                return
            yield line_number, start, line.rstrip(b"\r\n")

    def count_record(self) -> bool:
        if self.records_read >= self.limits.max_source_records:
            self.exhausted = True
            return False
        self.records_read += 1
        return True


def archive_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _locator(member: str, line_number: int, byte_offset: int, raw_line: bytes) -> SourceLocator:
    return SourceLocator(member, line_number, byte_offset, sha256(raw_line).hexdigest())


def _decode_ascii(raw: bytes, member: str, line_number: int) -> str:
    try:
        return raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise VocabularyError("MALFORMED_SOURCE",
                              f"non-ASCII source at {member}:{line_number}") from exc


def _split_marker(token: str) -> tuple[str, str | None]:
    for marker in MARKERS:
        if token.endswith(marker):
            return token[:-len(marker)], marker
    return token, None


def _read_forms(archive: tarfile.TarFile, pos: str, budget: _Budget,
                quota: int) -> tuple[list[FormRecord], int]:
    member_name = DATA_MEMBERS[pos]
    try:
        handle = archive.extractfile(member_name)
    except KeyError as exc:
        raise VocabularyError("MISSING_SOURCE_MEMBER", f"missing {member_name}") from exc
    require(handle is not None, "MISSING_SOURCE_MEMBER", f"missing {member_name}")
    records: list[FormRecord] = []
    excluded_collocations = 0
    with handle:
        for line_number, byte_offset, raw_line in budget.lines(handle):
            if len(records) >= quota or budget.exhausted:
                break
            if not raw_line[:1].isdigit():
                continue
            if not budget.count_record():
                break
            text = _decode_ascii(raw_line, member_name, line_number)
            fields = text.split(" | ", 1)[0].split()
            if len(fields) < 4:
                raise VocabularyError("MALFORMED_SOURCE", f"short data row at {member_name}:{line_number}")
            try:
                word_count = int(fields[3], 16)
            except ValueError as exc:
                raise VocabularyError("MALFORMED_SOURCE",
                                      f"invalid hexadecimal word count at {member_name}:{line_number}") from exc
            if word_count < 1 or len(fields) < 4 + word_count * 2:
                raise VocabularyError("MALFORMED_SOURCE",
                                      f"invalid word fields at {member_name}:{line_number}")
            synset_type = fields[2]
            if synset_type not in EXPECTED_TYPES[pos]:
                raise VocabularyError("MALFORMED_SOURCE",
                                      f"unexpected synset type at {member_name}:{line_number}")
            locator = _locator(member_name, line_number, byte_offset, raw_line)
            for position in range(word_count):
                raw_token = fields[4 + position * 2]
                lex_id = fields[5 + position * 2]
                form, marker = _split_marker(raw_token)
                if "_" in form:
                    excluded_collocations += 1
                    continue
                if not form:
                    raise VocabularyError("MALFORMED_SOURCE",
                                          f"empty word field at {member_name}:{line_number}")
                records.append(FormRecord(pos, fields[0], synset_type, position,
                                          raw_token, form, lex_id, marker, locator))
                if len(records) >= quota:
                    break
    return records, excluded_collocations


def _read_exceptions(archive: tarfile.TarFile, pos: str, budget: _Budget,
                     quota: int) -> list[ExceptionRecord]:
    if quota == 0:
        return []
    member_name = EXCEPTION_MEMBERS[pos]
    try:
        handle = archive.extractfile(member_name)
    except KeyError as exc:
        raise VocabularyError("MISSING_SOURCE_MEMBER", f"missing {member_name}") from exc
    require(handle is not None, "MISSING_SOURCE_MEMBER", f"missing {member_name}")
    records: list[ExceptionRecord] = []
    with handle:
        for line_number, byte_offset, raw_line in budget.lines(handle):
            if len(records) >= quota or budget.exhausted:
                break
            if not raw_line.strip():
                continue
            if not budget.count_record():
                break
            text = _decode_ascii(raw_line, member_name, line_number)
            fields = text.split()
            if len(fields) < 2:
                raise VocabularyError("MALFORMED_SOURCE",
                                      f"short exception row at {member_name}:{line_number}")
            inflected = fields[0]
            locator = _locator(member_name, line_number, byte_offset, raw_line)
            for position, base in enumerate(fields[1:]):
                if "_" in inflected or "_" in base:
                    continue
                records.append(ExceptionRecord(pos, inflected, base, position, locator))
                if len(records) >= quota:
                    break
    return records


def build_fragment_registry(model: NativeModel) -> tuple[tuple[FragmentRecord, ...], dict[str, object]]:
    """Create only the explicit fragments established before AUTH-17."""
    refs: dict[str, object] = {}
    records: list[FragmentRecord] = []
    for text in ("un", "he", "an", "et", "te", "er", "nd"):
        fragment_id = f"glyph.{text}"
        ref = model.define(Layer.GLYPH, ascii_symbols(text))
        refs[fragment_id] = ref
        records.append(FragmentRecord(fragment_id, text, "glyph", ref.definition_id,
                                      (), tuple(text.encode("ascii"))))
    component_specs = (
        ("component.ette", "ette", ("glyph.et", "glyph.te"), ()),
        ("component.hyphen-ette", "-ette", ("glyph.et", "glyph.te"), (45,)),
        ("component.un", "un", ("glyph.un",), ()),
        ("component.er", "er", ("glyph.er",), ()),
    )
    for fragment_id, text, children, literal_prefix in component_specs:
        native_children = tuple(SymbolRef(value) for value in literal_prefix) + tuple(refs[name] for name in children)
        ref = model.define(Layer.COMPONENT, native_children)
        refs[fragment_id] = ref
        records.append(FragmentRecord(fragment_id, text, "component", ref.definition_id,
                                      children, literal_prefix))
    return tuple(records), refs


def _candidates(fragments: tuple[FragmentRecord, ...], refs: dict[str, object]):
    layer_rank = {"glyph": Layer.GLYPH.value, "component": Layer.COMPONENT.value}
    rows = [(record.text.encode("ascii"), layer_rank[record.layer], record.fragment_id,
             refs[record.fragment_id]) for record in fragments if record.selectable]
    return tuple(sorted(rows, key=lambda row: (-len(row[0]), -row[1], row[2])))


def construct_word(model: NativeModel, text: str, fragments: tuple[FragmentRecord, ...],
                   refs: dict[str, object]) -> ConstructionRecord:
    try:
        encoded = text.encode("ascii", errors="strict")
    except UnicodeEncodeError as exc:
        raise VocabularyError("NON_ASCII_FORM", "safe-ASCII pilot cannot construct the form") from exc
    require(bool(encoded), "MALFORMED_SOURCE", "empty form cannot be constructed")
    candidates = _candidates(fragments, refs)
    children, pieces, offset = [], [], 0
    while offset < len(encoded):
        selected = next((row for row in candidates if encoded.startswith(row[0], offset)), None)
        if selected is None:
            value = encoded[offset]
            children.append(SymbolRef(value))
            pieces.append(ConstructionPiece("symbol", offset, offset + 1,
                                            chr(value), symbol_value=value))
            offset += 1
        else:
            data, _rank, fragment_id, ref = selected
            children.append(ref)
            pieces.append(ConstructionPiece("fragment", offset, offset + len(data),
                                            data.decode("ascii"), fragment_id=fragment_id))
            offset += len(data)
    ref = model.define(Layer.WORD, tuple(children))
    require(model.expand(ref) == encoded, "INVARIANT_ERROR", "native construction changed source bytes")
    return ConstructionRecord(text, ref.definition_id, tuple(pieces))


def build_pilot(archive_path: str | Path, limits: PilotLimits | None = None,
                expected_sha256: str = SOURCE_SHA256) -> tuple[PilotResult, NativeModel]:
    """Build one isolated pilot catalog. No caller model can be partially mutated."""
    path = Path(archive_path)
    require(path.is_file(), "SOURCE_NOT_FOUND", "WordNet archive does not exist")
    require(type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is not None,
            "VALIDATION_ERROR", "expected_sha256 must be a SHA-256 hex digest")
    actual_sha256 = archive_sha256(path)
    require(actual_sha256 == expected_sha256, "SOURCE_HASH_MISMATCH",
            "WordNet archive digest does not match the approved source")
    selected_limits = PilotLimits() if limits is None else limits
    require(type(selected_limits) is PilotLimits, "VALIDATION_ERROR", "limits must be PilotLimits")
    budget = _Budget(selected_limits)
    raw_forms: list[FormRecord] = []
    raw_exceptions: list[ExceptionRecord] = []
    excluded_collocations = 0
    completed_members: set[str] = set()
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            for pos in POS_ORDER:
                rows, excluded = _read_forms(archive, pos, budget, selected_limits.forms_per_pos)
                raw_forms.extend(rows)
                excluded_collocations += excluded
                if len(rows) >= selected_limits.forms_per_pos or not budget.exhausted:
                    completed_members.add(f"forms.{pos}")
                if budget.exhausted:
                    break
            if not budget.exhausted:
                for pos in POS_ORDER:
                    rows = _read_exceptions(archive, pos, budget,
                                            selected_limits.exception_pairs_per_pos)
                    raw_exceptions.extend(rows)
                    if len(rows) >= selected_limits.exception_pairs_per_pos or not budget.exhausted:
                        completed_members.add(f"exceptions.{pos}")
                    if budget.exhausted:
                        break
    except (tarfile.TarError, OSError) as exc:
        raise VocabularyError("MALFORMED_ARCHIVE", "cannot read approved WordNet archive") from exc

    model = NativeModel()
    fragments, refs = build_fragment_registry(model)
    by_text: dict[str, ConstructionRecord] = {}

    def construction(text: str) -> ConstructionRecord:
        if text not in by_text:
            by_text[text] = construct_word(model, text, fragments, refs)
        return by_text[text]

    forms = tuple(replace(record,
                          definition_id=construction(record.form).definition_id,
                          construction_id=construction(record.form).definition_id)
                  for record in raw_forms)
    exceptions = tuple(replace(record,
                               inflected_definition_id=construction(record.inflected).definition_id,
                               base_definition_id=construction(record.base).definition_id)
                       for record in raw_exceptions)
    shortages = {}
    for pos in POS_ORDER:
        form_short = selected_limits.forms_per_pos - sum(row.part_of_speech == pos for row in forms)
        exc_short = selected_limits.exception_pairs_per_pos - sum(row.part_of_speech == pos for row in exceptions)
        if form_short and f"forms.{pos}" not in completed_members:
            shortages[f"forms.{pos}"] = form_short
        if exc_short and f"exceptions.{pos}" not in completed_members:
            shortages[f"exceptions.{pos}"] = exc_short
    status = "PARTIAL" if shortages else "COMPLETE"
    result = PilotResult(status, actual_sha256, selected_limits, budget.bytes_read,
                         budget.records_read, forms, exceptions, fragments,
                         tuple(by_text[key] for key in sorted(by_text)),
                         MappingProxyType(shortages), excluded_collocations,
                         MappingProxyType(model.stats()))
    return result, model
