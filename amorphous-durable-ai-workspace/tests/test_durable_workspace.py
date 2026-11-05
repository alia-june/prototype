import json, shutil, tempfile, unittest
from pathlib import Path
from durable_workspace.canonical import CanonicalizationError, dumps, loads, sha256
from durable_workspace.workspace import DurableWorkspace, RecoveryError, SnapshotError

class DurableWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name)/"ws"; self.ws=DurableWorkspace.init(self.root)
    def tearDown(self): self.td.cleanup()

    def test_canonical_unicode_and_key_order(self):
        self.assertEqual(dumps({"b":1,"a":"e\u0301"}), '{"a":"é","b":1}')
    def test_float_rejected(self):
        with self.assertRaises(CanonicalizationError): dumps({"x":1.5})
    def test_set_get_delete_and_chain(self):
        self.ws.set("alpha", {"nested":[1,True,None,"x"]}); self.ws.set("alpha", {"v":2}); self.ws.delete("alpha")
        with self.assertRaises(KeyError): self.ws.get("alpha")
        r=self.ws.verify(); self.assertEqual(r["event_count"],3); self.assertEqual(r["record_count"],0)
    def test_snapshot_three_way_equality(self):
        self.ws.set("alpha", {"x":1}); self.ws.set("β\nkey", ["🙂", "nul\u0000tab\t", None, False])
        sd=self.ws.checkpoint(); r=DurableWorkspace.inspect_snapshot(sd)
        self.assertEqual(set(r["quorum_kinds"]), {"sqlite","jsonl","xml"}); self.assertTrue(r["manifest_digest_matches_quorum"])
    def test_recovery(self):
        self.ws.set("alpha", {"x":1}); self.ws.set("beta", [1,2,3]); sd=self.ws.checkpoint()
        recovered=DurableWorkspace.recover(sd, Path(self.td.name)/"recovered")
        self.assertEqual(recovered.get("alpha"), {"x":1}); self.assertEqual(recovered.verify()["event_count"],2)
    def test_recovery_one_corrupt_representation(self):
        self.ws.set("x", {"n":1}); sd=self.ws.checkpoint(); (sd/"snapshot.xml").write_text("<broken>",encoding="utf-8")
        recovered=DurableWorkspace.recover(sd, Path(self.td.name)/"r2"); self.assertEqual(recovered.get("x"), {"n":1})

    def test_recovery_with_corrupt_sqlite_uses_jsonl_xml(self):
        self.ws.set("x", {"n":1}); sd=self.ws.checkpoint()
        with (sd/"snapshot.sqlite3").open("r+b") as f:
            f.seek(100); f.write(b"CORRUPT")
        recovered=DurableWorkspace.recover(sd, Path(self.td.name)/"r_sqlite_bad")
        self.assertEqual(recovered.get("x"), {"n":1})
    def test_recovery_rejects_single_survivor(self):
        self.ws.set("x", 1); sd=self.ws.checkpoint(); (sd/"snapshot.xml").write_text("bad",encoding="utf-8"); (sd/"snapshot.jsonl").write_text("bad",encoding="utf-8")
        with self.assertRaises(RecoveryError): DurableWorkspace.recover(sd, Path(self.td.name)/"r3")
    def test_manifest_tamper_blocks_manifest_quorum_match(self):
        self.ws.set("x",1); sd=self.ws.checkpoint(); mp=sd/"manifest.json"; m=json.loads(mp.read_text()); m["logical_digest"]="0"*64; mp.write_text(json.dumps(m),encoding="utf-8")
        r=DurableWorkspace.inspect_snapshot(sd); self.assertFalse(r["manifest_digest_matches_quorum"])
        with self.assertRaises(RecoveryError): DurableWorkspace.recover(sd, Path(self.td.name)/"r4")

if __name__=="__main__": unittest.main()
