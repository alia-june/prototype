"""Deterministic bounded WordNet record pull for the AUTH-18A probe."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import re
import tarfile

from .values import MapError, canonical, exact_integer, require


SOURCE_SHA256 = "3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a"
SELECTION_SEED = "etabit-auth18a-relative-drive-1"
MEMBERS = {"n": "dict/data.noun", "v": "dict/data.verb",
           "a": "dict/data.adj", "s": "dict/data.adj", "r": "dict/data.adv"}
MAX_LINE_BYTES = 1_048_576


@dataclass(frozen=True, slots=True)
class PullLimits:
    sample_records: int = 8
    max_targets: int = 32
    max_source_bytes: int = 4 * 1024 * 1024
    max_candidate_records: int = 50_000

    def __post_init__(self):
        exact_integer(self.sample_records, "sample_records", 1, 8)
        exact_integer(self.max_targets, "max_targets", 0, 32)
        exact_integer(self.max_source_bytes, "max_source_bytes", 1, 4 * 1024 * 1024)
        exact_integer(self.max_candidate_records, "max_candidate_records", 1, 50_000)

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class WordField:
    raw_token: str
    lex_id: str

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PointerField:
    pointer_index: int
    symbol: str
    target_offset: str
    target_pos: str
    source_target: str

    def to_record(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SourceRecord:
    member: str
    byte_offset: int
    line_number: int | None
    synset_offset: str
    lex_filenum: str
    synset_type: str
    words: tuple[WordField, ...]
    pointers: tuple[PointerField, ...]
    gloss: str
    raw_line: str
    raw_sha256: str
    record_id: str = field(init=False)

    def __post_init__(self):
        require(type(self.raw_line) is str and self.raw_line.encode("ascii", "strict") is not None,
                "MALFORMED_SOURCE", "source record must remain ASCII")
        require(self.synset_offset == f"{self.byte_offset:08d}", "SOURCE_OFFSET_MISMATCH",
                "record offset field does not equal member byte offset")
        object.__setattr__(self, "record_id", sha256(canonical(self.to_record())).hexdigest())

    def to_record(self) -> dict:
        return {"member": self.member, "byte_offset": self.byte_offset,
                "line_number": self.line_number, "synset_offset": self.synset_offset,
                "lex_filenum": self.lex_filenum, "synset_type": self.synset_type,
                "words": [word.to_record() for word in self.words],
                "pointers": [pointer.to_record() for pointer in self.pointers],
                "gloss": self.gloss, "raw_line": self.raw_line,
                "raw_sha256": self.raw_sha256}


@dataclass(frozen=True, slots=True)
class PullResult:
    archive_sha256: str
    seed: str
    limits: PullLimits
    candidate_records: int
    source_bytes_read: int
    selected_records: tuple[SourceRecord, ...]
    target_records: tuple[SourceRecord, ...]
    selected_scores: tuple[str, ...]
    unresolved_target_keys: tuple[str, ...]

    def to_summary(self) -> dict:
        return {"archive_sha256": self.archive_sha256, "seed": self.seed,
                "limits": self.limits.to_record(), "candidate_records": self.candidate_records,
                "source_bytes_read": self.source_bytes_read,
                "selected_records": len(self.selected_records),
                "resolved_target_records": len(self.target_records),
                "unresolved_target_keys": len(self.unresolved_target_keys)}


def _archive_sha(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_record(member: str, byte_offset: int, line_number: int | None,
                 raw_line: bytes) -> SourceRecord:
    require(len(raw_line) <= MAX_LINE_BYTES, "SOURCE_LINE_LIMIT", "source line exceeds limit")
    try:
        text = raw_line.rstrip(b"\r\n").decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise MapError("MALFORMED_SOURCE", "WordNet source line is not ASCII") from exc
    fields_text, separator, gloss = text.partition(" | ")
    require(bool(separator), "MALFORMED_SOURCE", "WordNet record lacks gloss separator")
    fields = fields_text.split()
    require(len(fields) >= 5, "MALFORMED_SOURCE", "WordNet record is too short")
    require(re.fullmatch(r"[0-9]{8}", fields[0]) is not None, "MALFORMED_SOURCE",
            "invalid synset offset")
    try:
        word_count = int(fields[3], 16)
    except ValueError as exc:
        raise MapError("MALFORMED_SOURCE", "invalid hexadecimal word count") from exc
    cursor = 4
    require(word_count >= 1 and len(fields) >= cursor + word_count * 2 + 1,
            "MALFORMED_SOURCE", "invalid word field count")
    words = tuple(WordField(fields[cursor + i * 2], fields[cursor + i * 2 + 1])
                  for i in range(word_count))
    cursor += word_count * 2
    try:
        pointer_count = int(fields[cursor], 10)
    except ValueError as exc:
        raise MapError("MALFORMED_SOURCE", "invalid pointer count") from exc
    cursor += 1
    require(pointer_count >= 0 and len(fields) >= cursor + pointer_count * 4,
            "MALFORMED_SOURCE", "invalid pointer field count")
    pointers = tuple(PointerField(i, fields[cursor + i * 4], fields[cursor + i * 4 + 1],
                                  fields[cursor + i * 4 + 2], fields[cursor + i * 4 + 3])
                     for i in range(pointer_count))
    return SourceRecord(member, byte_offset, line_number, fields[0], fields[1], fields[2],
                        words, pointers, gloss, text, sha256(text.encode("ascii")).hexdigest())


def _read_primary(archive: tarfile.TarFile, limits: PullLimits, seed: str):
    member_name = MEMBERS["a"]
    try:
        member = archive.getmember(member_name)
        handle = archive.extractfile(member)
    except KeyError as exc:
        raise MapError("MISSING_SOURCE_MEMBER", f"missing {member_name}") from exc
    require(handle is not None, "MISSING_SOURCE_MEMBER", f"missing {member_name}")
    require(member.size <= limits.max_source_bytes, "SOURCE_BUDGET_EXCEEDED",
            "primary adjective member exceeds approved byte budget")
    raw = handle.read(limits.max_source_bytes + 1)
    require(len(raw) == member.size, "MALFORMED_SOURCE", "primary member read is incomplete")
    candidates, offset, line_number = [], 0, 0
    by_offset = {}
    for line in raw.splitlines(keepends=True):
        line_number += 1
        start = offset
        offset += len(line)
        if not line[:1].isdigit():
            continue
        require(len(candidates) < limits.max_candidate_records, "SOURCE_RECORD_LIMIT",
                "candidate record limit exceeded")
        record = parse_record(member_name, start, line_number, line)
        score = sha256(seed.encode("ascii") + b"\0" + record.synset_offset.encode("ascii")
                       + b"\0" + line.rstrip(b"\r\n")).hexdigest()
        candidates.append((score, record))
        by_offset[record.synset_offset] = (line_number, line)
    require(len(candidates) >= limits.sample_records, "INSUFFICIENT_SOURCE",
            "not enough adjective records for the approved sample")
    selected = tuple(sorted(candidates, key=lambda row: (row[0], row[1].synset_offset))
                     [:limits.sample_records])
    return raw, selected, by_offset, len(candidates)


def pull_wordnet_sample(archive_path: str | Path, limits: PullLimits | None = None,
                        seed: str = SELECTION_SEED,
                        expected_sha256: str = SOURCE_SHA256) -> PullResult:
    path = Path(archive_path)
    require(path.is_file(), "SOURCE_NOT_FOUND", "WordNet archive does not exist")
    require(type(seed) is str and 1 <= len(seed) <= 128 and seed.isascii(),
            "VALIDATION_ERROR", "selection seed must be bounded ASCII text")
    require(type(expected_sha256) is str and re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is not None,
            "VALIDATION_ERROR", "expected source digest is invalid")
    actual = _archive_sha(path)
    require(actual == expected_sha256, "SOURCE_HASH_MISMATCH",
            "WordNet archive digest does not match approved source")
    selected_limits = PullLimits() if limits is None else limits
    require(type(selected_limits) is PullLimits, "VALIDATION_ERROR", "limits must be PullLimits")
    try:
        with tarfile.open(path, mode="r:gz") as archive:
            primary, selected_rows, adjective_by_offset, candidate_count = _read_primary(
                archive, selected_limits, seed)
            selected_records = tuple(row[1] for row in selected_rows)
            selected_scores = tuple(row[0] for row in selected_rows)
            source_bytes = len(primary)
            target_keys = []
            for record in selected_records:
                for pointer in record.pointers:
                    key = f"{pointer.target_pos}:{pointer.target_offset}"
                    if key not in target_keys:
                        target_keys.append(key)
            chosen_keys = target_keys[:selected_limits.max_targets]
            unresolved = list(target_keys[selected_limits.max_targets:])
            target_records = []
            selected_ids = {record.record_id for record in selected_records}
            seen_ids = set(selected_ids)
            handles = {}
            try:
                for key in chosen_keys:
                    pos, target_offset = key.split(":", 1)
                    member_name = MEMBERS.get(pos)
                    if member_name is None:
                        unresolved.append(key)
                        continue
                    if member_name == MEMBERS["a"]:
                        located = adjective_by_offset.get(target_offset)
                        if located is None:
                            unresolved.append(key)
                            continue
                        line_number, raw_line = located
                    else:
                        if member_name not in handles:
                            handle = archive.extractfile(member_name)
                            require(handle is not None, "MISSING_SOURCE_MEMBER", f"missing {member_name}")
                            handles[member_name] = handle
                        handle = handles[member_name]
                        handle.seek(int(target_offset))
                        raw_line = handle.readline(MAX_LINE_BYTES + 1)
                        line_number = None
                        source_bytes += len(raw_line)
                        if source_bytes > selected_limits.max_source_bytes:
                            unresolved.append(key)
                            source_bytes -= len(raw_line)
                            continue
                    try:
                        record = parse_record(member_name, int(target_offset), line_number, raw_line)
                    except MapError:
                        unresolved.append(key)
                        continue
                    if record.record_id not in seen_ids:
                        target_records.append(record)
                        seen_ids.add(record.record_id)
            finally:
                for handle in handles.values():
                    handle.close()
    except (tarfile.TarError, OSError) as exc:
        raise MapError("MALFORMED_ARCHIVE", "cannot read WordNet archive") from exc
    return PullResult(actual, seed, selected_limits, candidate_count, source_bytes,
                      selected_records, tuple(target_records), selected_scores,
                      tuple(unresolved))
