#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("xosg_runtime", BASE / "runtime" / "xosg.py")
x = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = x
SPEC.loader.exec_module(x)


class Sandbox:
    def __enter__(self):
        self.td = tempfile.TemporaryDirectory(prefix="xosg-test-")
        self.root = Path(self.td.name)
        (self.root / "workspace").mkdir()
        (self.root / "machine").mkdir()
        (self.root / "machine" / "xOSG-0_machine_v1.2.0.json").write_text(
            (BASE / "machine" / "xOSG-0_machine_v1.2.0.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        self.saved = {k: getattr(x, k) for k in ["ROOT", "WORKSPACE", "STATE", "REG", "JOURNAL", "LOCK", "MACHINE"]}
        x.ROOT = self.root
        x.WORKSPACE = self.root / "workspace"
        x.STATE = x.WORKSPACE / "runtime_state.json"
        x.REG = x.WORKSPACE / "registers.json"
        x.JOURNAL = x.WORKSPACE / ".transaction.json"
        x.LOCK = x.WORKSPACE / ".runtime.lock"
        x.MACHINE = self.root / "machine" / "xOSG-0_machine_v1.2.0.json"
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(x, k, v)
        self.td.cleanup()


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args, **kwargs)


class CoreTests(unittest.TestCase):
    def test_default_state_valid(self):
        self.assertEqual(x.validate_state_obj(x.default_state()), [])

    def test_default_registers_valid(self):
        self.assertEqual(x.validate_registers_obj(x.default_registers()), [])

    def test_initialize_validate(self):
        with Sandbox():
            quiet(x.initialize)
            self.assertEqual(quiet(x.validate), 0)

    def test_initialize_sets_revision(self):
        with Sandbox():
            quiet(x.initialize)
            d = json.loads(x.STATE.read_text())
            self.assertEqual(d["artifact_revision"], x.REVISION)

    def test_task_reaches_decompose(self):
        with Sandbox():
            quiet(x.initialize)
            quiet(x.accept_task, "example")
            d = json.loads(x.STATE.read_text())
            self.assertEqual(d["state"], "DECOMPOSE")
            self.assertEqual(d["task"]["objective"], "example")

    def test_task_does_not_claim_execution(self):
        with Sandbox():
            quiet(x.initialize)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                x.accept_task("do external thing")
            self.assertIn("No external action was executed", buf.getvalue())

    def test_repeated_task_is_operational(self):
        with Sandbox():
            quiet(x.initialize)
            for i in range(20):
                quiet(x.accept_task, f"task {i}")
            self.assertEqual(quiet(x.validate), 0)

    def test_unicode_persists(self):
        with Sandbox():
            quiet(x.initialize)
            s = "café 中文 العربية हिन्दी 😀 e\u0301"
            quiet(x.accept_task, s)
            d = json.loads(x.STATE.read_text(encoding="utf-8"))
            self.assertEqual(d["task"]["objective"], s)

    def test_shell_text_is_data(self):
        with Sandbox() as sb:
            quiet(x.initialize)
            sentinel = sb.root / "pwned"
            quiet(x.accept_task, f"; touch {sentinel}")
            self.assertFalse(sentinel.exists())

    def test_max_objective_accepted(self):
        with Sandbox():
            quiet(x.initialize)
            quiet(x.accept_task, "A" * x.MAX_OBJECTIVE_CHARS)
            self.assertEqual(quiet(x.validate), 0)

    def test_oversize_objective_rejected(self):
        with Sandbox():
            quiet(x.initialize)
            with self.assertRaises(x.ValidationError):
                quiet(x.accept_task, "A" * (x.MAX_OBJECTIVE_CHARS + 1))

    def test_non_text_objective_rejected(self):
        with Sandbox():
            quiet(x.initialize)
            with self.assertRaises(x.ValidationError):
                quiet(x.accept_task, 123)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.sb = Sandbox().__enter__()
        quiet(x.initialize)

    def tearDown(self):
        self.sb.__exit__(None, None, None)

    def mutate_state(self, **changes):
        d = json.loads(x.STATE.read_text())
        d.update(changes)
        x.STATE.write_text(json.dumps(d), encoding="utf-8")

    def test_null_verification_controlled(self):
        self.mutate_state(verification=None)
        self.assertEqual(quiet(x.validate), 1)

    def test_numeric_state_root_controlled(self):
        x.STATE.write_text("123", encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_list_state_root_controlled(self):
        x.STATE.write_text("[]", encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_truncated_state_controlled(self):
        x.STATE.write_text("{", encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_empty_state_controlled(self):
        x.STATE.write_bytes(b"")
        self.assertEqual(quiet(x.validate), 1)

    def test_truncated_register_controlled(self):
        x.REG.write_text("{", encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_empty_register_controlled(self):
        x.REG.write_bytes(b"")
        self.assertEqual(quiet(x.validate), 1)

    def test_extra_register_rejected(self):
        r = x.default_registers(); r["EXTRA"] = []
        x.REG.write_text(json.dumps(r), encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_missing_register_rejected(self):
        r = x.default_registers(); del r["TODO"]
        x.REG.write_text(json.dumps(r), encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_null_register_list_rejected(self):
        r = x.default_registers(); r["NOTES"] = None
        x.REG.write_text(json.dumps(r), encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_invalid_state_enum(self):
        self.mutate_state(state="BOGUS")
        self.assertEqual(quiet(x.validate), 1)

    def test_pass_in_idle_rejected(self):
        self.mutate_state(verification={"status": "PASS", "checks": []})
        self.assertEqual(quiet(x.validate), 1)

    def test_pass_in_verify_allowed(self):
        self.mutate_state(state="VERIFY", verification={"status": "PASS", "checks": []})
        self.assertEqual(quiet(x.validate), 0)

    def test_bad_verification_status(self):
        self.mutate_state(verification={"status": "MAYBE", "checks": []})
        self.assertEqual(quiet(x.validate), 1)

    def test_bad_checks_type(self):
        self.mutate_state(verification={"status": "NOT_RUN", "checks": None})
        self.assertEqual(quiet(x.validate), 1)

    def test_bad_history_type(self):
        self.mutate_state(history=None)
        self.assertEqual(quiet(x.validate), 1)

    def test_history_bound(self):
        self.mutate_state(history=[{}] * (x.MAX_HISTORY + 1))
        self.assertEqual(quiet(x.validate), 1)

    def test_machine_corruption_controlled(self):
        x.MACHINE.write_text("{", encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_machine_identity_rejected(self):
        x.MACHINE.write_text(json.dumps({"system": {"id": "other"}}), encoding="utf-8")
        self.assertEqual(quiet(x.validate), 1)

    def test_bom_state_controlled(self):
        x.STATE.write_bytes(b"\xef\xbb\xbf{}")
        self.assertEqual(quiet(x.validate), 1)

    def test_invalid_utf8_controlled(self):
        x.STATE.write_bytes(b"\xff\xfe\xfd")
        self.assertEqual(quiet(x.validate), 1)

    def test_oversize_state_controlled(self):
        x.STATE.write_bytes(b" " * (x.MAX_JSON_BYTES + 1))
        self.assertEqual(quiet(x.validate), 1)

    def test_status_on_corruption_controlled(self):
        x.STATE.write_text("{", encoding="utf-8")
        self.assertEqual(quiet(x.status), 1)

    def test_task_on_corruption_is_controlled_exception(self):
        x.STATE.write_text("{", encoding="utf-8")
        with self.assertRaises(x.DataCorruptionError):
            quiet(x.accept_task, "task")


class TransitionTests(unittest.TestCase):
    def test_all_configured_allowed_transitions(self):
        for old, news in x.ALLOWED_TRANSITIONS.items():
            for new in news:
                st = x.default_state(); st["state"] = old
                x.transition(st, new)
                self.assertEqual(st["state"], new)

    def test_representative_illegal_transitions(self):
        samples = [("IDLE", "DELIVER"), ("INTAKE", "VERIFY"), ("DECOMPOSE", "DELIVER"), ("LOG", "EXECUTE")]
        for old, new in samples:
            st = x.default_state(); st["state"] = old
            with self.assertRaises(x.ValidationError):
                x.transition(st, new)

    def test_history_is_bounded_during_transition(self):
        st = x.default_state(); st["history"] = [{}] * x.MAX_HISTORY; st["state"] = "IDLE"
        x.transition(st, "INTAKE")
        self.assertEqual(len(st["history"]), x.MAX_HISTORY)


class PersistenceTests(unittest.TestCase):
    def test_valid_journal_recovery(self):
        with Sandbox():
            quiet(x.initialize)
            state = x.default_state(); state["state"] = "INTAKE"
            regs = x.default_registers(); regs["NOTES"].append({"recovered": True})
            x.save_json(x.JOURNAL, x._journal_payload(state, regs))
            x.STATE.write_text("{}", encoding="utf-8")
            recovered, _ = x.recover_if_needed()
            self.assertTrue(recovered)
            self.assertEqual(json.loads(x.STATE.read_text())["state"], "INTAKE")
            self.assertFalse(x.JOURNAL.exists())

    def test_bad_journal_checksum_fails_closed(self):
        with Sandbox():
            quiet(x.initialize)
            j = x._journal_payload(x.default_state(), x.default_registers())
            j["sha256"] = "0" * 64
            x.save_json(x.JOURNAL, j)
            with self.assertRaises(x.DataCorruptionError):
                x.recover_if_needed()

    def test_bad_journal_shape_fails_closed(self):
        with Sandbox():
            quiet(x.initialize)
            x.save_json(x.JOURNAL, {"sha256": "x"})
            with self.assertRaises(x.DataCorruptionError):
                x.recover_if_needed()

    def test_commit_removes_journal(self):
        with Sandbox():
            quiet(x.initialize)
            self.assertFalse(x.JOURNAL.exists())

    def test_commit_leaves_no_tmp(self):
        with Sandbox():
            quiet(x.initialize)
            self.assertEqual(list(x.WORKSPACE.glob("*.tmp")), [])
            self.assertEqual(list(x.WORKSPACE.glob(".*.tmp")), [])

    def test_lock_timeout(self):
        with Sandbox():
            x.LOCK.write_text("held", encoding="utf-8")
            os.utime(x.LOCK, None)
            with self.assertRaises(x.LockTimeoutError):
                with x.runtime_lock(timeout=0.08):
                    pass

    def test_stale_lock_recovered(self):
        with Sandbox():
            x.LOCK.write_text("stale", encoding="utf-8")
            old = time.time() - x.LOCK_STALE_SECONDS - 5
            os.utime(x.LOCK, (old, old))
            with x.runtime_lock(timeout=0.2):
                self.assertTrue(x.LOCK.exists())
            self.assertFalse(x.LOCK.exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unsupported")
    def test_state_symlink_refused(self):
        with Sandbox() as sb:
            target = sb.root / "target.json"; target.write_text("{}")
            os.symlink(target, x.STATE)
            r = x.load_json(x.STATE)
            self.assertFalse(r.ok)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink unsupported")
    def test_lock_symlink_refused(self):
        with Sandbox() as sb:
            target = sb.root / "locktarget"; target.write_text("x")
            os.symlink(target, x.LOCK)
            with self.assertRaises(x.DataCorruptionError):
                with x.runtime_lock(timeout=0.02):
                    pass


class CLITests(unittest.TestCase):
    def test_cli_help(self):
        r = subprocess.run([sys.executable, str(BASE / "runtime" / "xosg.py"), "--help"], capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0)
        self.assertIn("validate", r.stdout)

    def test_cli_compile(self):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(BASE / "runtime" / "xosg.py")], capture_output=True, text=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
