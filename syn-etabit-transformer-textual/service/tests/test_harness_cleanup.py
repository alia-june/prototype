"""AUTH-16: owned Windows job completion and immediate log release."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from docstream_cpu.harness import runner

ROOT = Path(__file__).resolve().parents[2] / ".docstream/harness-repair-runs/auth19b-20261031/cleanup-cycles"


def save(path, value):
    raw = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with path.open("xb") as file: file.write(raw)
    return sha256(raw).hexdigest()


def fixture_worker(role, gate, ready):
    for path in (gate, ready):
        if not path.resolve().is_relative_to(ROOT.resolve()): raise ValueError("fixture output escaped owned area")
    if role == "leaf":
        save(ready, {"pid": os.getpid(), "parent_pid": os.getppid(), "log_inherited": True})
        print("owned leaf ready", flush=True)
    elif role in ("ready", "exited"):
        until = time.monotonic() + 8
        while not gate.exists():
            if time.monotonic() >= until: raise RuntimeError("fixture assignment gate not opened")
            time.sleep(.005)
        subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--fixture-worker", "leaf", str(gate), str(ready)],
                         stdout=sys.stdout, stderr=sys.stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        if role == "exited": return
    elif role != "early": raise ValueError("unknown closed fixture role")
    time.sleep(600)


class FakeJob:
    def __init__(self, events): self.events = events
    def Close(self): self.events.append("job_handle_closed")


class FakeProcess:
    def __init__(self, events): self.events, self.returncode = events, None
    def poll(self): return self.returncode
    def kill(self): self.events.append("launcher_killed"); self.returncode = 2
    def wait(self, timeout): self.events.append("launcher_reaped"); self.returncode = 2; return 2


@unittest.skipUnless(os.name == "nt", "Windows job/log cleanup contract")
class HarnessCleanupTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / (self._testMethodName + "-" + uuid4().hex)
        self.root.mkdir(parents=True, exist_ok=False)

    def actor(self):
        events = []
        actor = runner.OwnedProcess.__new__(runner.OwnedProcess)
        actor.job = FakeJob(events); actor.process = FakeProcess(events)
        actor.job_assigned = True
        actor.cleanup_evidence = {"status": "pending"}
        return actor, events

    def test_waits_for_job_zero_before_closing_handle_and_is_idempotent(self):
        import win32job
        actor, events = self.actor()
        counts = iter((2, 1, 0))
        def query(*args):
            if args[1] == win32job.JobObjectBasicProcessIdList: return ()
            count = next(counts); events.append("active-" + str(count)); return {"ActiveProcesses": count}
        with patch.object(win32job, "QueryInformationJobObject", side_effect=query), \
             patch.object(win32job, "TerminateJobObject", side_effect=lambda *args: events.append("termination_requested")), \
             patch.object(runner.time, "sleep"):
            actor.close()
            evidence = dict(actor.cleanup_evidence)
            actor.close()
        save(self.root / "observed.json", {"events": events, "cleanup": actor.cleanup_evidence})
        self.assertIn("active-0", events)
        self.assertLess(events.index("active-0"), events.index("job_handle_closed"))
        self.assertEqual(events.count("job_handle_closed"), 1)
        self.assertEqual(actor.cleanup_evidence, evidence)
        self.assertEqual(evidence["status"], "confirmed")
        self.assertEqual(evidence["active_processes_after"], 0)

    def test_job_timeout_is_explicit_and_cannot_turn_into_success_on_retry(self):
        import win32job
        actor, events = self.actor()
        with patch.object(win32job, "QueryInformationJobObject", side_effect=lambda job, kind: () if kind==win32job.JobObjectBasicProcessIdList else {"ActiveProcesses": 1}), \
             patch.object(win32job, "TerminateJobObject"), \
             patch.object(runner.time, "monotonic", side_effect=(0, 0, 6, 6)), \
             patch.object(runner.time, "sleep"):
            with self.assertRaises(RuntimeError) as first: actor.close()
            with self.assertRaises(RuntimeError): actor.close()
        save(self.root / "observed.json", {"events": events, "cleanup": actor.cleanup_evidence, "error": str(first.exception)})
        self.assertEqual(type(first.exception).__name__, "CleanupError")
        self.assertEqual(actor.cleanup_evidence["status"], "failed")
        self.assertIn("job_handle_closed", events)
        self.assertIn("launcher_reaped", events)

    def test_query_failure_is_not_reported_as_confirmed_cleanup(self):
        import win32job
        actor, events = self.actor()
        with patch.object(win32job, "QueryInformationJobObject", side_effect=OSError("controlled query failure")):
            with self.assertRaises(RuntimeError) as caught: actor.close()
        save(self.root / "observed.json", {"events": events, "cleanup": actor.cleanup_evidence, "error": str(caught.exception)})
        self.assertEqual(actor.cleanup_evidence["status"], "failed")
        self.assertIn("controlled query failure", str(caught.exception))
        self.assertIn("job_handle_closed", events)
        self.assertIn("launcher_reaped", events)

    def test_process_wait_timeout_is_an_explicit_cleanup_failure(self):
        import win32api, win32con, win32event, win32job
        actor, events = self.actor(); process_handle = FakeJob(events)
        query = lambda job, kind: (123,) if kind==win32job.JobObjectBasicProcessIdList else {"ActiveProcesses": 1}
        with patch.object(win32job, "QueryInformationJobObject", side_effect=query), \
             patch.object(win32job, "TerminateJobObject"), \
             patch.object(win32job, "IsProcessInJob", return_value=True), \
             patch.object(win32api, "OpenProcess", return_value=process_handle), \
             patch.object(win32event, "WaitForSingleObject", return_value=win32con.WAIT_TIMEOUT):
            with self.assertRaises(runner.CleanupError) as caught: actor.close()
        save(self.root / "observed.json", {"events": events, "cleanup": actor.cleanup_evidence, "error": str(caught.exception)})
        self.assertEqual(actor.cleanup_evidence["status"], "failed")
        self.assertIn("did not signal exit", str(caught.exception))
        self.assertIn("launcher_reaped", events)

    def test_pid_that_is_not_in_owned_job_is_not_waited(self):
        import win32api, win32event, win32job
        actor, events = self.actor(); process_handle = FakeJob(events)
        query = lambda job, kind: (123,) if kind==win32job.JobObjectBasicProcessIdList else {"ActiveProcesses": 0}
        with patch.object(win32job, "QueryInformationJobObject", side_effect=query), \
             patch.object(win32job, "IsProcessInJob", return_value=False), \
             patch.object(win32api, "OpenProcess", return_value=process_handle), \
             patch.object(win32event, "WaitForSingleObject") as wait:
            actor.close()
            wait.assert_not_called()
        save(self.root / "observed.json", {"events": events, "cleanup": actor.cleanup_evidence})
        self.assertEqual(actor.cleanup_evidence["process_ids_observed"], [])
        self.assertEqual(actor.cleanup_evidence["status"], "confirmed")

    def test_twenty_four_owned_cleanup_cycles_release_logs_without_retry(self):
        import win32file, win32con, win32job
        started = time.monotonic(); records = []
        modes = ("early",) * 8 + ("ready",) * 8 + ("exited",) * 8
        with (self.root / "events.jsonl").open("xb", buffering=0) as journal:
            for n, mode in enumerate(modes):
                self.assertLess(time.monotonic() - started, 600)
                folder = self.root / f"cycle-{n:02d}"; folder.mkdir()
                case = {"schema": "docstream.harness-cleanup.case/1", "case_id": f"cleanup-{n:02d}", "mode": mode,
                        "ready_seconds": 8, "cleanup_seconds": 5, "expected": "owned job zero and immediate exclusive log open"}
                digest = save(folder / "input.json", case)
                row = {"case_id": case["case_id"], "mode": mode, "input_sha256": digest, "status": "STARTED"}
                journal.write(json.dumps(row).encode() + b"\n")
                gate, ready, log_path = folder / "gate", folder / "ready.json", folder / "child.log"
                with log_path.open("xb") as log:
                    actor = runner.OwnedProcess([sys.executable, str(Path(__file__).resolve()), "--fixture-worker", mode, str(gate), str(ready)], log)
                    row["owned_launcher_pid"] = actor.process.pid
                    try:
                        if mode != "early":
                            gate.write_bytes(b"assigned\n")
                            deadline = time.monotonic() + 8
                            while not ready.exists() and time.monotonic() < deadline: time.sleep(.005)
                            self.assertTrue(ready.exists(), "owned descendant not ready")
                            row["descendant"] = json.loads(ready.read_text())
                            if mode == "exited": actor.process.wait(timeout=8)
                            row["launcher_exited_before_cleanup"] = actor.process.poll() is not None
                        row["active_before_cleanup"] = win32job.QueryInformationJobObject(actor.job, win32job.JobObjectBasicAccountingInformation)["ActiveProcesses"]
                    finally: actor.close()
                # Probe first: writing diagnostic evidence here could itself
                # delay the measurement enough to conceal a release race.
                try:
                    handle = win32file.CreateFile(str(log_path), win32con.GENERIC_READ, 0, None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL, None)
                    handle.Close()
                except Exception as exc:
                    row.update(cleanup=actor.cleanup_evidence, status="FAIL", exclusive_log_open=False,
                               error={"type":type(exc).__name__,"message":str(exc)})
                    save(folder / "result.json", row)
                    journal.write(json.dumps(row).encode() + b"\n")
                    raise
                row["cleanup"] = actor.cleanup_evidence
                self.assertEqual(row["cleanup"]["status"], "confirmed")
                self.assertEqual(row["cleanup"]["active_processes_after"], 0)
                self.assertEqual(row["cleanup"]["launch"]["strategy"], "windows_suspended_job")
                self.assertTrue(row["cleanup"]["launch"]["job_assigned_before_resume"])
                self.assertIsNotNone(actor.process.poll())
                # No retry, deletion or artificial delay hides a held log.
                row.update(status="PASS", exclusive_log_open=True)
                save(folder / "result.json", row); records.append(row)
                journal.write(json.dumps(row).encode() + b"\n")
                self.assertLess(sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file()), 512*1024*1024)
        save(self.root / "summary.json", {"status": "PASS", "cycles": len(records), "cases": records, "elapsed_seconds": round(time.monotonic()-started, 6)})
        self.assertEqual(len(records), 24)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fixture-worker":
        if len(sys.argv) != 5: raise ValueError("fixture needs role and two owned paths")
        fixture_worker(sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]))
    else: unittest.main()
