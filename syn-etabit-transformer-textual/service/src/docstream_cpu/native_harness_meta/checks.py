"""Closed synthetic faults and reproducible mutations of harness inputs/reports."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import threading
import time
from unittest.mock import patch
from uuid import uuid4

from ..native import Edit, NativeError, NativeModel, ascii_symbols
from ..native_harness import HARNESS_VERSION
from ..native_harness import cases as target_cases, core as target, runner as target_runner
from ..native_harness.workloads import execute as product_execute, make, rejection

SERVICE = Path(__file__).resolve().parents[3]
RUNS = SERVICE.parent / ".docstream" / "native-harness-meta-runs"


def encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def must(condition, message):
    if not condition:
        raise AssertionError(message)


@dataclass
class Context:
    root: Path
    seed: int = 20261030
    artifacts: list[str] = field(default_factory=list)
    terminations: int = 0


def sample():
    return next(target_cases.fuzzy_cases(20261030, 5))


def fake_report(ctx, mutation="clean"):
    """Controlled worker double: real source files are never edited."""
    def simulated(command, log_path, seconds, evidence_root, max_bytes):
        log_path.write_bytes(b"controlled meta-test worker double; no child launched\n")
        root = Path(command[command.index("--root") + 1])
        root.mkdir()
        (root / "inputs").mkdir()
        rows, events = [], []
        for n, case in enumerate(target_cases.fuzzy_cases(20261030, 5)):
            filename = f"inputs/{n:04d}-{case['case_id']}.json"
            raw = encode(case) + b"\n"
            (root / filename).write_bytes(raw)
            row = {"case_id": case["case_id"], "family": case["family"], "input": filename,
                   "input_sha256": sha256(raw).hexdigest(), "status": "PASS", "details": {}}
            rows.append(row)
            events.append({"event": "case_started", **row, "status": "STARTED"})
            events.append({"event": "case_finished", **deepcopy(row)})
        summary = {"schema": HARNESS_VERSION, "mode": "fuzzy-error", "status": "PASS",
                   "incomplete_reason": None, "cases": rows, "passed": 5, "failed": 0,
                   "submitted_transformation_attempts": 2, "elapsed_seconds": 0.0}
        if mutation == "failure_journal":
            events[1].update(status="FAIL", error={"type": "SyntheticProductError", "message": "deliberately failed actor", "tag": "synthetic"})
        elif mutation == "pending_journal":
            events.pop()
        elif mutation == "tampered_input":
            (root / rows[0]["input"]).write_bytes(b"{}\n")
        elif mutation == "missing_input":
            # Only this newly created fixture input is removed, not prior evidence.
            owned = root / rows[0]["input"]
            must(owned.resolve().is_relative_to(root.resolve()), "fixture path escaped")
            owned.unlink()
        elif mutation == "wrong_counts":
            summary["passed"] = 99
        elif mutation == "wrong_schema":
            summary["schema"] = "unknown.report/999"
        elif mutation == "wrong_identity":
            rows[0]["case_id"] = "different-id"
        elif mutation == "outside_input":
            rows[0]["input"] = "../outside.json"
        elif mutation == "duplicate_row":
            rows[1] = deepcopy(rows[0])
        elif mutation == "bad_middle_event":
            events.insert(3, None)
        events.append({"event": "mode_finished", "status": "PASS", "incomplete_reason": None})
        with (root / "events.jsonl").open("wb") as handle:
            for event in events:
                handle.write((encode(event) if event is not None else b"{malformed-middle") + b"\n")
        (root / "summary.json").write_bytes(encode(summary) + b"\n")
        return {"owned_pid": None, "exit_code": 0, "owned_child_stopped": True,
                "supervisor_reason": None, "simulated": True}

    with patch.object(target_runner, "supervise", side_effect=simulated):
        code, root, result = target_runner.run("fuzzy-error", seed=20261030, fuzzy_count=5,
            seconds=30, run_id="auth14-meta-double-" + uuid4().hex)
    ctx.artifacts.append(str(root))
    return code, root, result


def recover_failed_then_pass(ctx):
    folder = ctx.root / ("journal-" + uuid4().hex)
    folder.mkdir()
    row = {"case_id": "one", "status": "FAIL", "error": {"message": "synthetic failure"}}
    events = [{"event": "case_started", "case_id": "one"}, {"event": "case_failed", **row},
              {"event": "case_finished", **row, "status": "PASS"}]
    (folder / "events.jsonl").write_bytes(b"".join(encode(e) + b"\n" for e in events))
    recovered = target_runner.recover_mode(folder, "fuzzy-error", "controlled interruption")
    must(recovered["status"] == "FAIL", "an observed failure was demoted by a later PASS event")
    return {"observed": recovered["status"]}


def mutation_cases(seed=20261030, count=1000):
    rnd = random.Random(seed)
    for n in range(count):
        original = sample()
        item = {"id": f"mutation-{n:04d}", "mode": "fuzzy", "input": {}, "expected": "CONFIG_ERROR"}
        if n % 5 == 4:
            item.update(input={"kind": "valid", "case": original}, expected="PASS")
        else:
            kind = (n - n // 5) % 20
            value = deepcopy(original)
            if kind == 0: value["command"] = "__import__('os').system('never run')"
            elif kind == 1: value["schema"] = "unknown/" + str(rnd.randrange(1000))
            elif kind == 2:
                raw = encode(value)[:-1] + b',"seed":1}'
                item["input"] = {"kind": "raw", "raw_hex": raw.hex()}
            elif kind == 3: value["mode"] = "shell"
            elif kind == 4: value["family"] = "exec"
            elif kind == 5: value["case_id"] = "../" + str(rnd.randrange(10000))
            elif kind == 6: value["seed"] = True
            elif kind == 7: value["expected"]["exception"] = "Exception"
            elif kind == 8: value["expected"]["code"] = "ANY_EXCEPTION"
            elif kind == 9: value["input"]["recipe"] = "import_module"
            elif kind == 10: value["input"] = {"recipe": "literal_highbyte", "variant": 0, "value": "not-hex"}
            elif kind == 11: value["input"] = {"recipe": "resource", "variant": 0, "value": 999}
            elif kind == 12: value["expected"]["extra"] = "forbidden"
            elif kind == 13: item["input"] = {"kind": "raw", "raw_hex": b'{"seed":NaN}'.hex()}
            elif kind == 14: item["input"] = {"kind": "raw", "raw_hex": b'\xff\xfe{'.hex()}
            elif kind == 15: item["input"] = {"kind": "raw", "raw_hex": encode(value)[:rnd.randrange(1, 15)].hex()}
            elif kind == 16:
                value = target_cases.case("unknown", "hardening", "probe", {"name": "os.system"})
            elif kind == 17:
                value["expected"]["code"] = "INVALID_PATH"
                item.update(input={"kind": "oracle", "case": value}, expected="FAIL")
            elif kind == 18: item.update(input={"kind": "report", "mutation": "failure_journal"}, expected="FAIL")
            else: item.update(input={"kind": "recovery"}, expected="FAIL")
            if not item["input"]: item["input"] = {"kind": "raw", "raw_hex": encode(value).hex()}
        yield item


def execute_mutation(item, ctx):
    data, expected = item["input"], item["expected"]
    kind = data["kind"]
    if kind == "report":
        _, _, result = fake_report(ctx, data["mutation"])
        must(result["status"] == expected, "contradictory worker report was accepted or misclassified")
        return {"observed": result["status"], "synthetic": True}
    if kind == "recovery": return recover_failed_then_pass(ctx)
    if kind == "raw":
        path = ctx.root / ("replay-" + uuid4().hex + ".json")
        path.write_bytes(bytes.fromhex(data["raw_hex"]))
        try:
            target.load_case(path)
        except (ValueError, TypeError, RecursionError, UnicodeError):
            return {"observed": "CONFIG_ERROR"}
        raise AssertionError("malformed replay data was accepted")
    value = data["case"]
    if kind == "valid":
        target.validate_case(value)
        result = product_execute(value, target.Budget(), ctx.root)
        must(result["expected_rejection"], "valid control was not executed as declared")
        return {"observed": "PASS"}
    journal = target.Journal(ctx.root / ("oracle-" + uuid4().hex), "fuzzy-error", target.Budget())
    journal.record(value, product_execute)
    result = journal.finish()
    must(result["status"] == "FAIL", "incorrect expected error was not detected")
    return {"observed": result["status"], "synthetic": True}


HARDENING = (
    "closed_replay", "size_limit", "duplicate_json", "unicode_retention", "preexecution_input",
    "wrong_exception", "wrong_error_code", "wrong_bytes", "state_mutation", "failure_reduction",
    "shrink_interruption", "attempt_limit", "evidence_limit", "config_path", "non_overwrite",
    "report_failure_journal", "report_pending_journal", "report_tampered_input", "report_missing_input",
    "report_wrong_counts", "report_wrong_schema", "report_wrong_identity", "report_outside_input",
    "report_duplicate_row", "report_bad_middle_event", "failure_precedence", "truncated_tail",
    "product_identity_guard")


def run_hardening(name, ctx):
    if name.startswith("report_"):
        mutation = name[len("report_"):]
        _, _, result = fake_report(ctx, mutation)
        if mutation == "failure_journal":
            must(result["status"] == "FAIL", "journal failure became an unqualified PASS")
        else:
            must(result["status"] != "PASS", "unverified or contradictory report became PASS: " + mutation)
        return {"observed": result["status"], "synthetic": True}
    if name == "failure_precedence": return recover_failed_then_pass(ctx)
    if name in ("closed_replay", "duplicate_json"):
        item = next(x for x in mutation_cases(ctx.seed, 5) if x["input"].get("raw_hex"))
        if name == "duplicate_json": item["input"]["raw_hex"] = b'{"x":1,"x":2}'.hex()
        return execute_mutation(item, ctx)
    if name == "size_limit":
        file = ctx.root / "oversize.json"; file.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        try: target.load_case(file)
        except ValueError: return {"observed": "CONFIG_ERROR"}
        raise AssertionError("over-size replay accepted")
    if name == "unicode_retention":
        value = target_cases.error_case("literal_unicode", 1, random.Random(ctx.seed))
        file = ctx.root / "surrogate.json"; target.save(file, value)
        must(b"\\ud800" in file.read_bytes() and target.load_case(file) == value, "surrogate source was rewritten")
        return {"observed": "PASS"}
    if name == "config_path":
        for run_id in ("../escape", "A/B", "A\\B"):
            try: target_runner.run(run_id=run_id)
            except ValueError: continue
            raise AssertionError("output path traversal accepted")
        return {"observed": "CONFIG_ERROR"}
    if name == "non_overwrite":
        _, root, _ = fake_report(ctx)
        before = (root / "REPORT.md").read_bytes()
        try: target_runner.run("fuzzy-error", run_id=root.name)
        except FileExistsError: pass
        else: raise AssertionError("existing evidence overwritten")
        must((root / "REPORT.md").read_bytes() == before, "existing report changed")
        return {"observed": "CONFIG_ERROR"}
    if name == "product_identity_guard":
        calls = 0
        def hashes():
            nonlocal calls
            calls += 1
            return {"controlled-product.py": "before" if calls == 1 else "after"}
        with patch.object(target_runner, "source_hashes", side_effect=hashes):
            _, _, result = fake_report(ctx)
        must(result["status"] == "FAIL", "changed product identity did not fail the run")
        return {"observed": "FAIL", "synthetic": True}
    if name == "truncated_tail":
        folder = ctx.root / "truncated"; folder.mkdir()
        (folder / "events.jsonl").write_bytes(encode({"event": "case_started", "case_id": "one"}) + b'\n{"partial":')
        result = target_runner.recover_mode(folder, "fuzzy-error", "test interruption")
        must(result["status"] == "INCOMPLETE", "incomplete journal became PASS")
        return {"observed": result["status"]}
    journal = target.Journal(ctx.root / "subject", "fuzzy-error", target.Budget())
    value = sample()
    if name == "preexecution_input":
        def actor(case, budget, root):
            paths = list((root / "inputs").glob("*.json"))
            must(len(paths) == 1 and target.load_case(paths[0]) == case, "input not saved before execute")
            return product_execute(case, budget, root)
    elif name in ("wrong_exception", "wrong_error_code", "state_mutation"):
        def actor(case, budget, root):
            model, base = make()
            def corrupt():
                if name == "state_mutation": model.apply_batch(base.stream_id, (Edit("x", "replace", (), 0, 1, ascii_symbols("X")),))
                if name == "wrong_exception": raise KeyError("controlled wrong exception")
                raise NativeError("INVALID_PATH" if name == "wrong_error_code" else "VALIDATION_ERROR", "synthetic")
            return rejection(model, corrupt, {"exception": "NativeError", "code": "VALIDATION_ERROR"})
    elif name == "wrong_bytes":
        value = next(x for x in target_cases.fuzzy_cases(ctx.seed, 5) if x["family"] == "valid")
        def actor(case, budget, root):
            with patch.object(NativeModel, "expand_stream", return_value=b"deliberately wrong"):
                return product_execute(case, budget, root)
    elif name in ("failure_reduction", "shrink_interruption"):
        value = target_cases.error_case("operation_id", 3, random.Random(ctx.seed))
        calls = 0
        def actor(case, budget, root):
            nonlocal calls
            calls += 1
            if name == "shrink_interruption" and calls > 1: raise target.Incomplete("controlled shrinking cutoff")
            raise target.CheckFailed("synthetic", "controlled failure")
    elif name == "attempt_limit":
        journal.events.close()
        budget = target.Budget(max_attempts=1); model, base = make()
        try: budget.apply(model, base.stream_id, (Edit("a", "remove", (), 0, 1), Edit("b", "remove", (), 0, 1)))
        except target.Incomplete: return {"observed": "INCOMPLETE", "submitted": budget.attempts}
        raise AssertionError("attempt budget not enforced")
    else:  # evidence_limit
        journal.events.close()
        journal = target.Journal(ctx.root / "tiny", "fuzzy-error", target.Budget(max_bytes=10))
        try: journal.record(value, product_execute)
        except target.Incomplete:
            result = journal.finish("controlled evidence cutoff")
            must(result["status"] == "INCOMPLETE", "evidence cutoff became PASS")
            return {"observed": result["status"]}
        raise AssertionError("evidence budget not enforced")
    reason = None
    try: journal.record(value, actor)
    except target.Incomplete: reason = "controlled cutoff"
    result = journal.finish(reason)
    expected = "PASS" if name == "preexecution_input" else "FAIL"
    must(result["status"] == expected, "synthetic fault was not classified correctly: " + name)
    if name == "failure_reduction":
        must(result["cases"][0].get("reduced_replay"), "reduced failure not retained")
    return {"observed": result["status"], "synthetic": name != "preexecution_input"}


TORTURE = ("parallel_smokes", "ready_timeouts", "early_timeouts", "interrupted_journals",
           "shrinking_budget", "shared_attempt_budget", "long_journal", "isolated_evidence")


def run_torture(name, ctx):
    if name == "parallel_smokes":
        def run_one(n):
            code, root, result = target_runner.run("fuzzy-error", fuzzy_count=5, seconds=30,
                run_id="auth14-meta-parallel-" + uuid4().hex)
            must(code == 0 and result["status"] == "PASS", "isolated concurrent smoke failed")
            return str(root)
        with ThreadPoolExecutor(max_workers=4) as pool: roots = list(pool.map(run_one, range(4)))
        must(len(set(roots)) == 4, "concurrent runs shared an evidence root")
        ctx.artifacts.extend(roots)
        return {"parallel_runs": 4, "all_passed": True}
    if name in ("ready_timeouts", "early_timeouts"):
        from ..harness.runner import OwnedProcess
        outcomes = []
        for n in range(8):
            folder = ctx.root / f"cycle-{n}"; folder.mkdir()
            marker = folder / "ready.json"
            # The target's private worker deliberately writes only to its own run tree.
            native_folder = target.RUNS / ("auth14-meta-timeout-" + uuid4().hex)
            native_folder.mkdir(); ctx.artifacts.append(str(native_folder))
            command = [sys.executable, "-m", "docstream_cpu.native_harness.worker", "--stall-ready", str(native_folder / "ready.json")]
            if name == "early_timeouts":
                result = target_runner.supervise(command, folder / "child.log", 0.02, folder, 512 * 1024 * 1024)
                must(result["supervisor_reason"] is not None and result["owned_child_stopped"], "early deadline did not clean up")
            else:
                with (folder / "child.log").open("xb") as log:
                    owned = OwnedProcess(command, log)
                    try:
                        deadline = time.monotonic() + 8
                        while not (native_folder / "ready.json").exists() and time.monotonic() < deadline:
                            must(owned.process.poll() is None, "stalled worker exited before readiness")
                            time.sleep(0.01)
                        must((native_folder / "ready.json").exists(), "stalled worker not ready")
                    finally: target_runner.stop_owned(owned)
                    must(owned.process.poll() is not None, "ready child remained active")
                result = {"owned_pid": owned.process.pid, "owned_child_stopped": True, "expected_status": "INCOMPLETE"}
            ctx.terminations += 1; outcomes.append(result)
        return {"cycles": 8, "owned_terminations": 8, "all_stopped": True, "outcomes": outcomes}
    if name == "interrupted_journals":
        for n in range(20): recover_failed_then_pass(ctx)
        return {"failure_precedence_recoveries": 20}
    if name == "shrinking_budget":
        for n in range(8):
            sub = Context(ctx.root / f"shrink-{n}", ctx.seed); sub.root.mkdir()
            run_hardening("shrink_interruption", sub)
        return {"interrupted_shrinks": 8, "failure_retained": True}
    if name == "shared_attempt_budget":
        budget = target.Budget(max_attempts=20); model, base = make()
        lock, results = threading.Lock(), []
        def caller(n):
            for k in range(10):
                try:
                    budget.apply(model, base.stream_id, (Edit(f"c{n}-{k}", "replace", (), 0, 1, ascii_symbols("X")),))
                    with lock: results.append("accepted")
                except target.Incomplete:
                    with lock: results.append("cutoff")
        with ThreadPoolExecutor(max_workers=4) as pool: list(pool.map(caller, range(4)))
        must(budget.attempts == 20 and results.count("accepted") == 20 and results.count("cutoff") == 20,
             "concurrent attempt budget drifted")
        return {"submitted": 20, "cutoffs": 20, "callers": 4}
    if name == "long_journal":
        folder = ctx.root / "long"; folder.mkdir()
        with (folder / "events.jsonl").open("wb") as file:
            for n in range(2000):
                file.write(encode({"event": "case_finished", "case_id": str(n), "status": "PASS"}) + b"\n")
        result = target_runner.recover_mode(folder, "fuzzy-error", "unfinished mode")
        must(result["status"] == "INCOMPLETE", "unfinished long journal became PASS")
        return {"events": 2000, "observed": result["status"]}
    roots = []
    for _ in range(8):
        _, root, result = fake_report(ctx)
        must(result["status"] == "PASS", "clean evidence control failed")
        roots.append(root)
    must(len(set(roots)) == 8, "evidence roots collided")
    return {"isolated_runs": 8}
