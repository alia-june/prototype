from __future__ import annotations

from hashlib import sha256
import io
import json
from pathlib import Path
import random
import tarfile
import tempfile
import time
import unittest

from docstream_cpu.relative_maps import (MapDraft, MapEntry, MapError, MapLimits,
                                         MapRef, PullLimits, RelativeMapStore,
                                         build_probe, pull_wordnet_sample,
                                         verify_probe, write_probe)


def entry(kind="value", **payload):
    return MapEntry.create(kind, payload or {"value": "x"})


def make_wordnet_archive(root: Path, adjective_records: int = 12) -> tuple[Path, str]:
    noun = b"00000000 00 n 01 entity 0 000 | target noun\n"
    header = b"  synthetic fixture\n"
    rows, offset = [], len(header)
    for index in range(adjective_records):
        line = (f"{offset:08d} 00 a 01 adj{index} 0 001 @ 00000000 n 0000 | adjective {index}\n"
                .encode("ascii"))
        rows.append(line)
        offset += len(line)
    members = {"dict/data.adj": header + b"".join(rows), "dict/data.noun": noun}
    path = root / "wordnet.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            info.mtime = 0
            archive.addfile(info, io.BytesIO(payload))
    return path, sha256(path.read_bytes()).hexdigest()


def basic_composition_store():
    store = RelativeMapStore()
    refs = store.publish_batch((
        MapDraft("objects", "objects", "objects", 1, "test", (), (entry(),)),
        MapDraft("order.a", "orders", "order-a", 1, "test", ("objects",),
                 (entry("order", object_ids=["a", "b"], positions=[0, 1]),)),
        MapDraft("order.b", "orders", "order-b", 1, "test", ("objects",),
                 (entry("order", object_ids=["b", "a"], positions=[0, 1]),)),
        MapDraft("drive.a", "composed", "drive", 1, "test", ("objects", "order.a"),
                 (entry("composition", role="adjective"),)),
        MapDraft("drive.b", "composed", "drive", 1, "test", ("objects", "order.b"),
                 (entry("composition", role="adjective"),)),
        MapDraft("context.a1", "context", "context-a", 1, "context-a", ("drive.a",),
                 (entry("selection", role="adjective", selected_input_index=0),)),
        MapDraft("context.b1", "context", "context-b", 1, "context-b", ("drive.a",),
                 (entry("selection", role="adjective", selected_input_index=0),)),
        MapDraft("replace", "replacement-ledger", "replacement", 1, "context-a",
                 ("drive.a", "drive.b", "context.a1"),
                 (entry("replacement", prior_input_index=0, replacement_input_index=1),)),
        MapDraft("context.a2", "context", "context-a", 2, "context-a",
                 ("drive.b", "context.a1", "replace"),
                 (entry("selection", role="adjective", selected_input_index=0),)),
    ))
    return store, refs


class RelativeMapRigidTests(unittest.TestCase):
    def assert_code(self, code, action):
        with self.assertRaises(MapError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_entry_is_canonical_content_addressed_and_detached(self):
        first = MapEntry.create("example", {"b": 2, "a": [1]})
        second = MapEntry.create("example", {"a": [1], "b": 2})
        self.assertEqual(first, second)
        self.assertEqual(first.entry_id, second.entry_id)
        detached = first.payload
        detached["a"].append(9)
        self.assertEqual(first.payload, {"a": [1], "b": 2})
        self.assert_code("NON_CANONICAL_ENTRY",
                         lambda: MapEntry("example", '{"b":2,"a":[1]}'))

    def test_identical_recipe_reuses_identity_and_changed_order_changes_it(self):
        store, refs = basic_composition_store()
        self.assertNotEqual(refs["drive.a"], refs["drive.b"])
        duplicate = store.publish_batch((MapDraft(
            "duplicate", "composed", "drive", 1, "test",
            (refs["objects"].map_id, refs["order.a"].map_id),
            (entry("composition", role="adjective"),)),))
        self.assertEqual(duplicate["duplicate"], refs["drive.a"])
        self.assertEqual(store.stats()["maps"], 9)

    def test_context_replacement_is_relative_and_non_destructive(self):
        store, refs = basic_composition_store()
        self.assertEqual(store.resolve_role(refs["context.a1"], "adjective"), refs["drive.a"])
        self.assertEqual(store.resolve_role(refs["context.a2"], "adjective"), refs["drive.b"])
        self.assertEqual(store.resolve_role(refs["context.b1"], "adjective"), refs["drive.a"])
        self.assertEqual(store.definition(refs["drive.a"]).name, "drive")
        self.assertIn(refs["drive.a"], store.lineage(refs["context.a2"]))

    def test_batch_cycle_rejects_without_publication(self):
        store = RelativeMapStore()
        before = store.stats()
        drafts = (MapDraft("a", "objects", "a", 1, "test", ("b",), (entry(),)),
                  MapDraft("b", "objects", "b", 1, "test", ("a",), (entry(),)))
        self.assert_code("DEPENDENCY_CYCLE", lambda: store.publish_batch(drafts))
        self.assertEqual(store.stats(), before)

    def test_dangling_input_and_duplicate_key_reject_atomically(self):
        store = RelativeMapStore()
        before = store.stats()
        self.assert_code("UNKNOWN_INPUT", lambda: store.publish_batch((
            MapDraft("a", "objects", "a", 1, "test", ("missing",), (entry(),)),)))
        self.assertEqual(store.stats(), before)
        draft = MapDraft("same", "objects", "a", 1, "test", (), (entry(),))
        self.assert_code("DUPLICATE_DRAFT_KEY", lambda: store.publish_batch((draft, draft)))
        self.assertEqual(store.stats(), before)

    def test_invalid_context_selection_is_explicit(self):
        store = RelativeMapStore()
        before = store.stats()
        self.assert_code("INVALID_SELECTION", lambda: store.publish_batch((
            MapDraft("objects", "objects", "objects", 1, "test", (), (entry(),)),
            MapDraft("context", "context", "context", 1, "test", ("objects",),
                     (entry("selection", role="adjective", selected_input_index=9),)),)))
        self.assertEqual(store.stats(), before)

    def test_invalid_order_positions_reject_before_publication(self):
        store = RelativeMapStore()
        before = store.stats()
        self.assert_code("INVALID_ORDER", lambda: store.publish_batch((
            MapDraft("objects", "objects", "objects", 1, "test", (), (entry(),)),
            MapDraft("order", "orders", "order", 1, "test", ("objects",),
                     (entry("order", object_ids=["a", "b"], positions=[1, 0]),)),)))
        self.assertEqual(store.stats(), before)

    def test_public_views_are_immutable_snapshots(self):
        store = RelativeMapStore()
        refs = store.publish_batch((MapDraft("a", "objects", "a", 1, "test", (), (entry(),)),))
        snapshot = store.definitions
        with self.assertRaises(TypeError):
            snapshot[refs["a"].map_id] = store.definition(refs["a"])
        store.publish_batch((MapDraft("b", "objects", "b", 1, "test", (), (entry(),)),))
        self.assertEqual(len(snapshot), 1)
        self.assertEqual(store.stats()["maps"], 2)

    def test_limit_failure_keeps_state(self):
        store = RelativeMapStore(MapLimits(max_maps=1))
        store.publish_batch((MapDraft("a", "objects", "a", 1, "test", (), (entry(),)),))
        before = store.stats()
        self.assert_code("LIMIT_EXCEEDED", lambda: store.publish_batch((
            MapDraft("b", "objects", "b", 1, "test", (), (entry(),)),)))
        self.assertEqual(store.stats(), before)

    def test_synthetic_probe_is_deterministic_and_preserves_source_relations(self):
        with tempfile.TemporaryDirectory() as raw:
            source, digest = make_wordnet_archive(Path(raw))
            first, store = build_probe(source, digest)
            second, _ = build_probe(source, digest)
        self.assertEqual(first.to_summary(), second.to_summary())
        self.assertEqual(dict(first.aliases), dict(second.aliases))
        self.assertEqual(first.relation_records, second.relation_records)
        self.assertEqual(first.pull.candidate_records, 12)
        self.assertEqual(len(first.pull.selected_records), 8)
        self.assertEqual(len(first.pull.target_records), 1)
        self.assertTrue(all(row["resolution_status"] == "resolved"
                            for row in first.relation_records))
        self.assertEqual(store.stats()["maps"], 21)

    def test_source_digest_and_byte_budget_are_enforced(self):
        with tempfile.TemporaryDirectory() as raw:
            source, digest = make_wordnet_archive(Path(raw))
            self.assert_code("SOURCE_HASH_MISMATCH",
                             lambda: pull_wordnet_sample(source, expected_sha256="0" * 64))
            self.assert_code("SOURCE_BUDGET_EXCEEDED", lambda: pull_wordnet_sample(
                source, PullLimits(max_source_bytes=32), expected_sha256=digest))

    def test_target_cap_retains_unresolved_relations_without_guessing(self):
        with tempfile.TemporaryDirectory() as raw:
            source, digest = make_wordnet_archive(Path(raw))
            result = pull_wordnet_sample(source, PullLimits(max_targets=0),
                                         expected_sha256=digest)
        self.assertEqual(len(result.target_records), 0)
        self.assertEqual(result.unresolved_target_keys, ("n:00000000",))

    def test_changed_seed_selects_a_different_replayable_sample(self):
        with tempfile.TemporaryDirectory() as raw:
            source, digest = make_wordnet_archive(Path(raw), adjective_records=30)
            first = pull_wordnet_sample(source, seed="seed-a", expected_sha256=digest)
            second = pull_wordnet_sample(source, seed="seed-b", expected_sha256=digest)
            replay = pull_wordnet_sample(source, seed="seed-a", expected_sha256=digest)
        self.assertEqual([row.record_id for row in first.selected_records],
                         [row.record_id for row in replay.selected_records])
        self.assertNotEqual([row.record_id for row in first.selected_records],
                            [row.record_id for row in second.selected_records])

    def test_pull_limits_reject_coercion_and_scope_expansion(self):
        for kwargs in [dict(sample_records=True), dict(sample_records=9),
                       dict(max_targets=33), dict(max_source_bytes=4 * 1024 * 1024 + 1),
                       dict(max_candidate_records=50_001)]:
            with self.subTest(kwargs=kwargs):
                self.assert_code("VALIDATION_ERROR", lambda: PullLimits(**kwargs))

    def test_evidence_round_trip_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source, digest = make_wordnet_archive(root)
            result, store = build_probe(source, digest)
            output = root / "evidence"
            write_probe(output, result, store, {"elapsed_seconds": 0.1})
            audit = verify_probe(source, output, digest)
            self.assertEqual(audit["status"], "PASS")
            maps = output / "maps.jsonl"
            maps.write_bytes(maps.read_bytes() + b"{}\n")
            self.assert_code("EVIDENCE_HASH_MISMATCH",
                             lambda: verify_probe(source, output, digest))


class RelativeMapFuzzyTests(unittest.TestCase):
    def test_seeded_200_invalid_batches_reject_without_state_change(self):
        rng = random.Random(20261030)
        counts = {name: 0 for name in ("unknown", "cycle", "duplicate", "missing-digest")}
        for case in range(200):
            family = rng.choice(tuple(counts))
            counts[family] += 1
            with self.subTest(case=case, family=family):
                store = RelativeMapStore()
                before = store.stats()
                if family == "unknown":
                    drafts = (MapDraft("a", "objects", "a", 1, "test", ("nope",), (entry(),)),)
                    code = "UNKNOWN_INPUT"
                elif family == "cycle":
                    drafts = (MapDraft("a", "objects", "a", 1, "test", ("b",), (entry(),)),
                              MapDraft("b", "objects", "b", 1, "test", ("a",), (entry(),)))
                    code = "DEPENDENCY_CYCLE"
                elif family == "duplicate":
                    one = MapDraft("a", "objects", "a", 1, "test", (), (entry(),))
                    drafts, code = (one, one), "DUPLICATE_DRAFT_KEY"
                else:
                    drafts = (MapDraft("a", "objects", "a", 1, "test", ("0" * 64,), (entry(),)),)
                    code = "UNKNOWN_INPUT"
                with self.assertRaises(MapError) as caught:
                    store.publish_batch(drafts)
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(store.stats(), before)
        self.assertTrue(all(value > 0 for value in counts.values()))


class RelativeMapTortureTests(unittest.TestCase):
    def test_500_map_chain_and_alternatives_remain_bounded_and_addressable(self):
        started = time.perf_counter()
        store = RelativeMapStore(MapLimits(max_maps=600, max_batch=128))
        previous = None
        all_refs = []
        for batch in range(5):
            drafts = []
            for index in range(100):
                key = f"m{batch:02d}.{index:03d}"
                input_keys = () if previous is None else (previous,)
                drafts.append(MapDraft(key, "structures", f"structure-{batch:02d}-{index:03d}",
                                       1, "torture", input_keys,
                                       (entry("node", batch=batch, index=index),)))
                previous = key
            refs = store.publish_batch(tuple(drafts))
            all_refs.extend(refs.values())
            previous = refs[f"m{batch:02d}.099"].map_id
        self.assertEqual(store.stats(), {"maps": 500, "entries": 500, "publications": 5})
        self.assertEqual(len(set(all_refs)), 500)
        self.assertEqual(len(store.lineage(all_refs[-1])), 500)
        self.assertLess(time.perf_counter() - started, 30.0)


if __name__ == "__main__":
    unittest.main()
