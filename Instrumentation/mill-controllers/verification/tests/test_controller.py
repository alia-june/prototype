#!/usr/bin/env python3
"""Bounded functional checks for the Mill batch verification controller."""
from __future__ import annotations

import importlib.util
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path(os.environ.get("MILL_FACTORY_ROOT", REPOSITORY_ROOT / "mill-factory"))
SPEC = importlib.util.spec_from_file_location("mill_verification_controller", ROOT / "controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(controller)

REFERENCE = os.environ.get("MILL_VERIFICATION_REFERENCE_BATCH")


@unittest.skipUnless(REFERENCE and Path(REFERENCE).is_dir(), "MILL_VERIFICATION_REFERENCE_BATCH must name an existing Mill batch")
class VerificationControllerTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        target = root / "batches" / Path(REFERENCE).name
        shutil.copytree(Path(REFERENCE), target)
        return target

    def request(self, batch: Path, request_id: str = "verify-test-001") -> dict:
        return {"request_id": request_id, "batch_path": str(batch)}

    def authority(self, request: dict, root: Path, identity: dict | None = None) -> dict:
        identity = identity or controller.source_identity(SOURCE_ROOT)
        return {
            "authority_id": "test-authority",
            "authorized_by": "bounded-test-harness",
            "request_digest": controller.request_digest(request),
            "tool_identity_sha256": identity["sha256"],
            "allowed_batch_roots": [str(root / "batches")],
        }

    def assert_no_leases(self, state: Path) -> None:
        connection = sqlite3.connect(state / "controller.sqlite3")
        try:
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM leases").fetchone()[0])
        finally:
            connection.close()

    def test_valid_hold_batch_reports_pass_without_mutating_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            before = (batch / "MANIFEST.sha256").read_bytes()
            request = self.request(batch)
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("PASS", receipt["validator"]["reported_result"])
            self.assertEqual(before, (batch / "MANIFEST.sha256").read_bytes())
            self.assertTrue((root / "state" / "receipts" / "verify-test-001.json").is_file())

    def test_disposable_manifest_tamper_is_retained_as_validator_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            with (batch / "README.md").open("a", encoding="utf-8") as output:
                output.write("\nIntentional disposable validation tamper.\n")
            request = self.request(batch, "verify-test-tamper")
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("FAIL", receipt["validator"]["reported_result"])
            self.assertEqual("review_validator_failures", receipt["next_permitted_action"])

    def test_outside_authorized_root_is_refused_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            request = self.request(batch, "verify-test-outside")
            authority = self.authority(request, root)
            authority["allowed_batch_roots"] = [str(root / "not-the-batches-root")]
            receipt = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertFalse(receipt["process"]["launched"])

    def test_changed_source_identity_is_refused_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            request = self.request(batch, "verify-test-identity")
            authority = self.authority(request, root)
            authority["tool_identity_sha256"] = "0" * 64
            receipt = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertFalse(receipt["process"]["launched"])

    def test_existing_controller_lease_blocks_competing_invocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            connection = controller.initialize(state)
            connection.execute("INSERT INTO leases VALUES (?, ?, ?)", (str(batch), "prior-holder", "now"))
            connection.close()
            request = self.request(batch, "verify-test-lease")
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertFalse(receipt["process"]["launched"])
            self.assertIn("verification lease held", receipt["problems"][0])

    def test_same_request_returns_prior_receipt_instead_of_reinvoking(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            request = self.request(batch, "verify-test-replay")
            authority = self.authority(request, root)
            first = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            second = controller.execute(request, authority, SOURCE_ROOT, root / "state", "pwsh")
            self.assertEqual("PASS", first["validator"]["reported_result"])
            self.assertTrue(second["replayed_request"])
            self.assertEqual(first["receipt_id"], second["receipt_id"])

    def test_corrupt_state_store_preserves_an_emergency_receipt_without_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            state.mkdir()
            (state / "controller.sqlite3").write_bytes(b"not a sqlite database")
            request = self.request(batch, "verify-test-corrupt-state")
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("emergency_receipt_retained", receipt["retained_state"])
            self.assertFalse(receipt["process"]["launched"])
            self.assertTrue((state / "emergency-receipts" / "verify-test-corrupt-state.json").is_file())

    def test_bounded_process_output_and_timeout_helpers(self):
        noisy = controller.bounded_run([sys.executable, "-c", "import sys; sys.stdout.write('x'*1100000)"], Path.cwd(), 10)
        self.assertTrue(noisy["stdout_truncated"])
        self.assertEqual(controller.MAX_CAPTURE_BYTES, len(noisy["stdout"].encode("utf-8")))
        delayed = controller.bounded_run([sys.executable, "-c", "import time; time.sleep(2)"], Path.cwd(), 0.05)
        self.assertTrue(delayed["timed_out"])

    def test_missing_launcher_retains_unknown_receipt_and_releases_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            request = self.request(batch, "verify-test-missing-launcher")
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "not-a-real-powershell")
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("unknown", receipt["validator"]["reported_result"])
            self.assertEqual("await_recovery_authority", receipt["next_permitted_action"])
            self.assertTrue((state / "receipts" / "verify-test-missing-launcher.json").is_file())
            self.assert_no_leases(state)

    def test_missing_batch_retains_unknown_receipt_and_releases_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = root / "batches" / "missing-batch"
            state = root / "state"
            request = self.request(batch, "verify-test-missing-batch")
            receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("permitted", receipt["admission"])
            self.assertEqual("unknown", receipt["validator"]["reported_result"])
            self.assertFalse(batch.exists())
            self.assert_no_leases(state)

    def test_request_id_cannot_be_reused_for_a_different_request(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            first = self.request(batch, "verify-test-collision")
            first_receipt = controller.execute(first, self.authority(first, root), SOURCE_ROOT, state, "pwsh")
            changed = self.request(root / "batches" / "other-batch", "verify-test-collision")
            receipt = controller.execute(changed, self.authority(changed, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("PASS", first_receipt["validator"]["reported_result"])
            self.assertEqual("not_permitted", receipt["admission"])
            self.assertIn("already bound", receipt["problems"][0])
            self.assertFalse(receipt["process"]["launched"])

    def test_post_validation_retention_failure_creates_emergency_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            request = self.request(batch, "verify-test-post-retention")
            initial_connection = controller.initialize(state)
            with mock.patch.object(
                controller,
                "initialize",
                side_effect=[initial_connection, sqlite3.OperationalError("forced post-validation state failure")],
            ):
                receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("emergency_receipt_retained", receipt["retained_state"])
            self.assertTrue((state / "emergency-receipts" / "verify-test-post-retention.json").is_file())

    def test_simulated_timeout_is_retained_as_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            request = self.request(batch, "verify-test-timeout")
            timed_out = {
                "launched": True, "exit_code": -9, "timed_out": True,
                "stdout": "", "stderr": "", "stdout_truncated": False, "stderr_truncated": False,
            }
            with mock.patch.object(controller, "bounded_run", return_value=timed_out):
                receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("unknown", receipt["validator"]["reported_result"])
            self.assertEqual("await_recovery_authority", receipt["next_permitted_action"])
            self.assert_no_leases(state)

    def test_malformed_validator_output_is_retained_as_unknown_not_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch = self.fixture(root)
            state = root / "state"
            request = self.request(batch, "verify-test-malformed-output")
            malformed = {
                "launched": True, "exit_code": 0, "timed_out": False,
                "stdout": "not JSON", "stderr": "", "stdout_truncated": False, "stderr_truncated": False,
            }
            with mock.patch.object(controller, "bounded_run", return_value=malformed):
                receipt = controller.execute(request, self.authority(request, root), SOURCE_ROOT, state, "pwsh")
            self.assertEqual("unknown", receipt["validator"]["reported_result"])
            self.assertEqual("await_recovery_authority", receipt["next_permitted_action"])
            self.assert_no_leases(state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
