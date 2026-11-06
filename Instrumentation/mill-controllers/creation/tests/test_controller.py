import importlib.util
import json
import sqlite3
import tempfile
import unittest
import sys
import os
import concurrent.futures
from pathlib import Path

CONTROLLER_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path(os.environ.get("MILL_FACTORY_ROOT", REPOSITORY_ROOT / "mill-factory"))
SPEC = importlib.util.spec_from_file_location("mill_controller", CONTROLLER_ROOT / "controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(controller)


class MillControllerTests(unittest.TestCase):
    def request(self, root: Path, request_id: str = "controller-test-001", slug: str = "controller-test"):
        return {
            "request_id": request_id,
            "slug": slug,
            "title": "Controller validation batch",
            "scope": "Validate the single-tool controller against the unchanged Mill source.",
            "date": "2026-11-05",
            "workspace_root": str(root),
            "output_root": str(root / "mill"),
            "owner": "controller-test",
        }

    def authority(self, request, tool_identity, root: Path):
        return {
            "authority_id": "controller-test-authority",
            "authorized_by": "controller-test",
            "request_digest": controller.request_digest(request),
            "tool_identity_sha256": tool_identity["sha256"],
            "allowed_output_roots": [str(root / "mill")],
        }

    def test_invalid_date_stops_before_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root)
            request["date"] = "2026-02-30"
            identity = controller.tree_identity(SOURCE_ROOT)
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertEqual("none_observed", receipt["retained_state"])
            self.assertFalse((root / "mill").exists())

    def test_mismatched_authority_stops_before_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root)
            identity = controller.tree_identity(SOURCE_ROOT)
            authority = self.authority(request, identity, root)
            authority["request_digest"] = "0" * 64
            receipt = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertFalse((root / "mill").exists())

    def test_mismatched_tool_identity_stops_before_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root)
            identity = controller.tree_identity(SOURCE_ROOT)
            authority = self.authority(request, identity, root)
            authority["tool_identity_sha256"] = "1" * 64
            receipt = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertIn("tool identity", receipt["problems"][0])
            self.assertFalse((root / "mill").exists())

    def test_normal_creation_is_verified_and_receipt_is_reopenable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root)
            identity = controller.tree_identity(SOURCE_ROOT)
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("true", receipt["creation_reported"])
            self.assertEqual("pass", receipt["artifact_verification"])
            self.assertEqual("promotion_pending", receipt["authority"])
            saved = json.loads((root / "state" / "receipts" / "controller-test-001.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["request_digest"], saved["request_digest"])
            self.assertTrue(Path(receipt["derived"]["batch_path"]).is_dir())

    def test_admission_only_never_creates_a_mill_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root, "controller-test-admit", "admit-test")
            identity = controller.tree_identity(SOURCE_ROOT)
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, root / "state", "pwsh", admit_only=True)
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("invoke", receipt["next_permitted_action"])
            self.assertFalse((root / "mill").exists())

    def test_nul_and_oversize_requests_stop_before_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            identity = controller.tree_identity(SOURCE_ROOT)
            nul_request = self.request(root, "controller-test-nul", "nul-test")
            nul_request["title"] = "bad\x00title"
            receipt = controller.execute(nul_request, self.authority(nul_request, identity, root), SOURCE_ROOT, root / "state-nul", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertIn("NUL", " ".join(receipt["problems"]))
            large_request = self.request(root, "controller-test-large", "large-test")
            large_request["scope"] = "x" * (controller.MAX_JSON_BYTES + 1)
            receipt = controller.execute(large_request, self.authority(large_request, identity, root), SOURCE_ROOT, root / "state-large", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertIn("exceeds", " ".join(receipt["problems"]))
            self.assertFalse((root / "mill").exists())

    def test_bounded_process_output_and_timeout(self):
        noisy = controller.bounded_run([sys.executable, "-c", "import sys; sys.stdout.write('x'*1100000)"], Path.cwd(), 10)
        self.assertTrue(noisy["stdout_truncated"])
        self.assertEqual(controller.MAX_CAPTURE_BYTES, len(noisy["stdout"].encode("utf-8")))
        delayed = controller.bounded_run([sys.executable, "-c", "import time; time.sleep(2)"], Path.cwd(), 0.05)
        self.assertTrue(delayed["timed_out"])

    def test_corrupt_state_store_writes_emergency_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            state.mkdir()
            (state / "controller.sqlite3").write_bytes(b"not a sqlite database")
            request = self.request(root, "controller-test-corrupt", "corrupt-test")
            identity = controller.tree_identity(SOURCE_ROOT)
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertTrue((state / "emergency-receipts" / "controller-test-corrupt.json").is_file())

    def test_concurrent_state_initialization_is_retried(self):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "state"
            def open_and_close(_):
                connection = controller.initialize(state)
                connection.close()
            with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
                list(pool.map(open_and_close, range(32)))

    def test_existing_lease_blocks_a_competing_request_without_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root, "controller-test-lease", "lease-test")
            identity = controller.tree_identity(SOURCE_ROOT)
            state = root / "state"
            connection = controller.initialize(state)
            mill_root, batch_path, _, _ = controller.derive(request)
            connection.execute("INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)",
                               ("prior-holder", "prior-digest", str(batch_path), "running", "{}", "now", "now"))
            connection.execute("INSERT INTO leases VALUES (?, ?, ?)", (str(batch_path), "prior-holder", "now"))
            connection.close()
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertIn("destination lease held", receipt["problems"][0])
            self.assertFalse(batch_path.exists())

    def test_allowed_root_comparison_uses_windows_case_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root, "controller-test-case", "case-test")
            identity = controller.tree_identity(SOURCE_ROOT)
            authority = self.authority(request, identity, root)
            authority["allowed_output_roots"] = [authority["allowed_output_roots"][0].upper()]
            receipt = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh", admit_only=True)
            self.assertEqual("permitted", receipt["admission"])

    def test_admission_only_stops_when_destination_lease_is_held(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root, "controller-test-admit-lease", "admit-lease")
            identity = controller.tree_identity(SOURCE_ROOT)
            state = root / "state"
            _, batch_path, _, _ = controller.derive(request)
            connection = controller.initialize(state)
            connection.execute("INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)",
                               ("prior-holder", "prior-digest", str(batch_path), "running", "{}", "now", "now"))
            connection.execute("INSERT INTO leases VALUES (?, ?, ?)", (str(batch_path), "prior-holder", "now"))
            connection.close()
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, state, "pwsh", admit_only=True)
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertEqual("await_recovery_authority", receipt["next_permitted_action"])
            self.assertIn("destination lease held", receipt["problems"][0])

    def test_launcher_failure_retains_receipt_and_releases_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request = self.request(root, "controller-test-launcher", "launcher-test")
            identity = controller.tree_identity(SOURCE_ROOT)
            state = root / "state"
            receipt = controller.execute(request, self.authority(request, identity, root), SOURCE_ROOT, state, "not-a-real-powershell")
            self.assertEqual("unknown", receipt["creation_reported"])
            self.assertEqual("recovery_pending", receipt["authority"])
            self.assertTrue((state / "receipts" / "controller-test-launcher.json").is_file())
            connection = sqlite3.connect(state / "controller.sqlite3")
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0])
            connection.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
