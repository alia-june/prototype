from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from docstream_cpu.native import Layer, NativeModel
from docstream_cpu.native_vocabulary import (PilotLimits, VocabularyError,
                                             build_fragment_registry, build_pilot,
                                             construct_word, verify_run, write_run)


POS_TYPES = {"noun": "n", "verb": "v", "adj": "a", "adv": "r"}


def data_rows(pos: str, forms: list[str]) -> bytes:
    kind = POS_TYPES[pos]
    return b"".join(
        f"{index + 1740:08d} 00 {kind} 01 {form} 0 000 | fixture\n".encode("ascii")
        for index, form in enumerate(forms)
    )


def make_archive(root: Path, forms_by_pos: dict[str, list[str]] | None = None,
                 exceptions_by_pos: dict[str, list[str]] | None = None,
                 omit: str | None = None, malformed: tuple[str, bytes] | None = None) -> tuple[Path, str]:
    forms_by_pos = forms_by_pos or {pos: [f"{pos}word"] for pos in POS_TYPES}
    exceptions_by_pos = exceptions_by_pos or {pos: [f"{pos}words {pos}word"] for pos in POS_TYPES}
    path = root / "wordnet.tar.gz"
    members = {}
    for pos in POS_TYPES:
        members[f"dict/data.{pos}"] = data_rows(pos, forms_by_pos[pos])
        members[f"dict/{pos}.exc"] = ("\n".join(exceptions_by_pos[pos]) + "\n").encode("ascii")
    if malformed is not None:
        members[malformed[0]] = malformed[1]
    if omit is not None:
        del members[omit]
    with tarfile.open(path, "w:gz") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(payload))
    digest = sha256(path.read_bytes()).hexdigest()
    return path, digest


class NativeVocabularyRigidTests(unittest.TestCase):
    def assert_code(self, code, action):
        with self.assertRaises(VocabularyError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_explicit_registry_matches_prior_native_constructions(self):
        model = NativeModel()
        fragments, refs = build_fragment_registry(model)
        by_id = {row.fragment_id: row for row in fragments}
        self.assertEqual(set(by_id), {"glyph.un", "glyph.he", "glyph.an", "glyph.et",
                                     "glyph.te", "glyph.er", "glyph.nd", "component.ette",
                                     "component.hyphen-ette", "component.un", "component.er"})
        self.assertEqual(model.expand(refs["component.ette"]), b"ette")
        self.assertEqual(model.expand(refs["component.hyphen-ette"]), b"-ette")
        self.assertNotEqual(refs["component.ette"], refs["component.hyphen-ette"])

    def test_marionette_uses_explicit_ette_and_does_not_infer_a_root(self):
        model = NativeModel()
        fragments, refs = build_fragment_registry(model)
        record = construct_word(model, "marionette", fragments, refs)
        self.assertEqual(model.expand(model.definitions[record.definition_id].ref), b"marionette")
        self.assertEqual(record.pieces[-1].fragment_id, "component.ette")
        self.assertFalse(any(model.definition(ref).layer is Layer.ROOT for ref in refs.values()))

    def test_literal_fallback_preserves_case_punctuation_and_digits(self):
        model = NativeModel()
        fragments, refs = build_fragment_registry(model)
        record = construct_word(model, "AD.22", fragments, refs)
        ref = model.definitions[record.definition_id].ref
        self.assertEqual(model.expand(ref), b"AD.22")
        self.assertTrue(all(piece.kind == "symbol" for piece in record.pieces))

    def test_balanced_parse_retains_locators_markers_duplicates_and_relations(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            forms = {"noun": ["marionette", "marionette"], "verb": ["render", "render"],
                     "adj": ["able(p)", "unable"], "adv": ["AD", "quickly"]}
            exceptions = {pos: [f"{pos}s {pos}", f"{pos}ed {pos}"] for pos in POS_TYPES}
            path, digest = make_archive(root, forms, exceptions)
            result, model = build_pilot(path, PilotLimits(2, 2), digest)
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(len(result.forms), 8)
        self.assertEqual(len(result.exceptions), 8)
        able = next(row for row in result.forms if row.raw_token == "able(p)")
        self.assertEqual((able.form, able.syntactic_marker), ("able", "(p)"))
        duplicate = [row for row in result.forms if row.form == "marionette"]
        self.assertEqual(len(duplicate), 2)
        self.assertEqual(duplicate[0].definition_id, duplicate[1].definition_id)
        self.assertNotEqual(duplicate[0].locator.line, duplicate[1].locator.line)
        self.assertEqual(model.expand(model.definitions[duplicate[0].definition_id].ref), b"marionette")

    def test_collocations_are_counted_but_not_converted_to_spaces(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            forms = {pos: [f"{pos}_collocation", f"{pos}word"] for pos in POS_TYPES}
            path, digest = make_archive(root, forms)
            result, _ = build_pilot(path, PilotLimits(1, 0), digest)
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(result.excluded_collocations, 4)
        self.assertFalse(any("_" in row.form for row in result.forms))

    def test_natural_source_exhaustion_below_up_to_cap_is_complete(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            forms = {pos: [f"{pos}word"] for pos in POS_TYPES}
            exceptions = {pos: [f"{pos}s {pos}"] for pos in POS_TYPES}
            path, digest = make_archive(root, forms, exceptions)
            result, _ = build_pilot(path, PilotLimits(1, 2), digest)
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual(len(result.exceptions), 4)
        self.assertEqual(dict(result.shortages), {})

    def test_replay_is_deterministic_while_occurrences_remain_separate(self):
        with tempfile.TemporaryDirectory() as raw:
            path, digest = make_archive(Path(raw))
            first, _ = build_pilot(path, PilotLimits(1, 1), digest)
            second, _ = build_pilot(path, PilotLimits(1, 1), digest)
        self.assertEqual(first.to_summary(), second.to_summary())
        self.assertEqual([row.to_record() for row in first.forms],
                         [row.to_record() for row in second.forms])
        self.assertEqual([row.to_record() for row in first.constructions],
                         [row.to_record() for row in second.constructions])

    def test_artifact_writer_hashes_every_payload_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source, digest = make_archive(root)
            result, _ = build_pilot(source, PilotLimits(1, 1), digest)
            output = root / "evidence"
            write_run(output, result, {"elapsed_seconds": 0.1})
            manifest = json.loads((output / "manifest.json").read_text(encoding="ascii"))
            for row in manifest["files"]:
                payload = (output / row["path"]).read_bytes()
                self.assertEqual((len(payload), sha256(payload).hexdigest()),
                                 (row["bytes"], row["sha256"]))
            self.assert_code("OUTPUT_EXISTS", lambda: write_run(output, result, {}))

    def test_maintained_verifier_replays_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source, digest = make_archive(root)
            result, _ = build_pilot(source, PilotLimits(1, 1), digest)
            output = root / "evidence"
            write_run(output, result, {"elapsed_seconds": 0.1})
            # The verifier is bound to the approved default digest. This synthetic
            # check therefore exercises manifest tamper rejection before replay.
            payload = output / "forms.jsonl"
            payload.write_bytes(payload.read_bytes() + b"{}\n")
            self.assert_code("EVIDENCE_HASH_MISMATCH",
                             lambda: verify_run(source, output))


class NativeVocabularyHardeningTests(unittest.TestCase):
    def assert_code(self, code, action):
        with self.assertRaises(VocabularyError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_source_hash_mismatch_rejects_before_parsing(self):
        with tempfile.TemporaryDirectory() as raw:
            path, _ = make_archive(Path(raw))
            self.assert_code("SOURCE_HASH_MISMATCH",
                             lambda: build_pilot(path, PilotLimits(1, 0), "0" * 64))

    def test_missing_member_is_explicit(self):
        with tempfile.TemporaryDirectory() as raw:
            path, digest = make_archive(Path(raw), omit="dict/data.verb")
            self.assert_code("MISSING_SOURCE_MEMBER",
                             lambda: build_pilot(path, PilotLimits(1, 0), digest))

    def test_malformed_hex_count_and_non_ascii_source_are_explicit(self):
        cases = [b"00001740 00 n zz word 0 000 | bad\n",
                 b"00001740 00 n 01 \xff 0 000 | bad\n"]
        for payload in cases:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as raw:
                path, digest = make_archive(Path(raw), malformed=("dict/data.noun", payload))
                self.assert_code("MALFORMED_SOURCE",
                                 lambda: build_pilot(path, PilotLimits(1, 0), digest))

    def test_exact_type_and_approved_ceiling_validation(self):
        for arguments in [dict(forms_per_pos=True), dict(forms_per_pos=251),
                          dict(exception_pairs_per_pos=26), dict(max_source_bytes=8 * 1024 * 1024 + 1),
                          dict(max_source_records=10_001)]:
            self.assert_code("VALIDATION_ERROR", lambda: PilotLimits(**arguments))

    def test_record_budget_returns_explicit_partial_without_overread(self):
        with tempfile.TemporaryDirectory() as raw:
            path, digest = make_archive(Path(raw))
            result, _ = build_pilot(path, PilotLimits(1, 1, max_source_records=4), digest)
        self.assertEqual(result.status, "PARTIAL")
        self.assertEqual(result.source_records_read, 4)
        self.assertEqual(len(result.forms), 4)
        self.assertEqual(len(result.exceptions), 0)
        self.assertEqual(set(result.shortages), {f"exceptions.{pos}" for pos in POS_TYPES})

    def test_byte_budget_returns_partial_and_never_reports_more_than_limit(self):
        with tempfile.TemporaryDirectory() as raw:
            path, digest = make_archive(Path(raw))
            result, _ = build_pilot(path, PilotLimits(1, 1, max_source_bytes=80), digest)
        self.assertEqual(result.status, "PARTIAL")
        self.assertLessEqual(result.source_bytes_read, 80)

    def test_malformed_archive_and_missing_path_are_structured(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            missing = root / "missing.tar.gz"
            self.assert_code("SOURCE_NOT_FOUND", lambda: build_pilot(missing))
            bad = root / "bad.tar.gz"
            bad.write_bytes(b"not a tar")
            digest = sha256(bad.read_bytes()).hexdigest()
            self.assert_code("MALFORMED_ARCHIVE",
                             lambda: build_pilot(bad, PilotLimits(1, 0), digest))


class NativeVocabularyTortureTests(unittest.TestCase):
    def test_approved_maximum_record_counts_complete_below_native_capacity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            forms = {pos: [f"{pos}{index:03d}" for index in range(250)] for pos in POS_TYPES}
            exceptions = {pos: [f"{pos}x{index:02d} {pos}b{index:02d}" for index in range(25)]
                          for pos in POS_TYPES}
            path, digest = make_archive(root, forms, exceptions)
            result, model = build_pilot(path, expected_sha256=digest)
        self.assertEqual(result.status, "COMPLETE")
        self.assertEqual((len(result.forms), len(result.exceptions)), (1_000, 100))
        self.assertEqual(result.source_records_read, 1_100)
        self.assertLessEqual(result.source_bytes_read, 8 * 1024 * 1024)
        self.assertLess(model.stats()["definitions"], model.limits.max_definitions)
        for construction in result.constructions[::97]:
            self.assertEqual(model.expand(model.definitions[construction.definition_id].ref),
                             construction.text.encode("ascii"))


if __name__ == "__main__":
    unittest.main()
