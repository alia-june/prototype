"""Assertions and bounded native workloads; never repairs the implementation."""
from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import threading
import time
from unittest.mock import patch

from docstream_cpu.native import (AssemblyRef, Edit, Layer, Limits, NativeError,
                                 NativeModel, SymbolRef, ascii_symbols)
from .core import check, fingerprint, save


def make(limits=None, data=b"abc"):
    model = NativeModel(limits)
    root = model.define(Layer.DOCUMENT, ascii_symbols(data))
    return model, model.create_stream(root)


def change(operation_id="change", data=b"X"):
    return Edit(operation_id, "replace", (), 0, 1, ascii_symbols(data))


def rejection(model, action, expected):
    before, state = fingerprint(model), model._state
    caught = None
    try:
        action()
    except Exception as exc:
        caught = exc
    actual_type = type(caught).__name__ if caught else None
    actual_code = getattr(caught, "code", None)
    check(fingerprint(model) == before and model._state is state, "state_changed",
          "rejected request changed retained state or counters", actual_type=actual_type, actual_code=actual_code)
    check(caught is not None, "unexpected_acceptance", "invalid request was accepted")
    check(type(caught) is (NativeError if expected["exception"] == "NativeError" else TypeError),
          "wrong_error_type", "rejection used an unexpected exception type", actual_type=actual_type, actual_code=actual_code)
    check(actual_code == expected["code"], "wrong_error_code", "rejection used an unexpected code",
          actual_type=actual_type, actual_code=actual_code)
    return {"expected_rejection": True, "exception": actual_type, "code": actual_code,
            "state_fingerprint_unchanged": True}


RESOURCE_LIMITS = ({"max_definitions": 1}, {"max_total_references": 3}, {"max_children": 3},
                   {"max_expanded_bytes": 3}, {"max_expansion_steps": 4}, {"max_streams": 1},
                   {"max_batches": 1}, {"max_operations": 1})


def run_error(case, budget):
    item, expected = case["input"], case["expected"]
    recipe, value = item["recipe"], item["value"]
    limits = Limits(**RESOURCE_LIMITS[value]) if recipe == "resource" else None
    model, base = make(limits)
    if recipe == "resource" and value == 6:
        budget.apply(model, base.stream_id, ())
    if recipe.startswith("symbol_"):
        action = lambda: SymbolRef(value)
    elif recipe == "literal_unicode" or recipe == "literal_long":
        action = lambda: ascii_symbols(value)
    elif recipe == "literal_highbyte":
        action = lambda: ascii_symbols(bytes.fromhex(value))
    elif recipe == "literal_mutable":
        action = lambda: ascii_symbols(bytearray.fromhex(value))
    elif recipe == "operation_id":
        action = lambda: Edit(value, "remove", (), 0, 1)
    elif recipe == "edit_type":
        action = lambda: Edit("bad", "remove", (), value, 1)
    elif recipe == "path_type":
        action = lambda: Edit("bad", "remove", (value,), 0, 1)
    elif recipe == "edit_shape":
        def action():
            if value == "execute":
                return Edit("bad", "execute")
            if value == "insert-count":
                return Edit("bad", "insert", (), 0, 1, ascii_symbols("X"))
            if value == "remove-refs":
                return Edit("bad", "remove", (), 0, 1, ascii_symbols("X"))
            return Edit("bad", "replace", (), 0, 1)
    elif recipe == "define_type":
        action = lambda: model.define(value, ascii_symbols("a"))
    elif recipe == "reference_missing":
        action = lambda: model.define(Layer.WORD, (AssemblyRef(value),))
    elif recipe == "reference_layer":
        action = lambda: model.define(Layer.GLYPH, (base.root,))
    elif recipe == "duplicate_batch":
        action = lambda: budget.apply(model, base.stream_id, (change("same"), change("same")))
    elif recipe == "batch_container":
        action = lambda: budget.apply(model, base.stream_id, value)
    elif recipe == "late_range":
        action = lambda: budget.apply(model, base.stream_id, (change(), Edit("late", "remove", (), value, 1)))
    elif recipe == "late_path":
        action = lambda: budget.apply(model, base.stream_id, (change(), Edit("late", "remove", (value,), 0, 1)))
    else:
        operations = (Edit("insert", "insert", (), 0, 0, ascii_symbols("X")),)
        if value in (0, 1):
            operations = (change(),)
        elif value == 7:
            operations = (change("one"), change("two", b"Y"))
        action = lambda: budget.apply(model, base.stream_id, operations)
    return rejection(model, action, expected)


def run_valid(case, budget):
    item = case["input"]
    original = bytes.fromhex(item["base_hex"])
    model, base = make(data=original)
    expected = bytearray(original)
    operations, prefixes = [], []
    for n, op in enumerate(item["operations"]):
        data = bytes.fromhex(op["data_hex"])
        operations.append(Edit(f"op{n}", op["kind"], (), op["index"], op["count"], ascii_symbols(data)))
        expected[op["index"]:op["index"] + op["count"]] = data
        prefixes.append(bytes(expected))
    result = budget.apply(model, base.stream_id, tuple(operations))
    for n in reversed(range(len(prefixes))):
        check(model.expand_stream(result.output_stream_ids[n]) == prefixes[n], "wrong_bytes", "prefix disagrees with byte oracle", prefix=n)
    check(model.expand_stream(base.stream_id) == original, "original_changed", "original stream changed")
    check(len(model.history(result.result_stream_id)) == len(operations) + 1, "wrong_history", "missing retained occurrence")
    return {"accepted": True, "prefixes_checked": len(prefixes), "result_hex": bytes(expected).hex()}


def fault_probe(name, budget, *, pressure=False):
    from docstream_cpu.native import model as implementation
    model, base = make(data=b"abc" * (100 if pressure else 1))
    current = base.stream_id
    if pressure:
        for n in range(3):
            current = budget.apply(model, current, (change(f"prepare{n}", bytes([88 + n])),)).result_stream_id
    before, state = fingerprint(model), model._state
    point = int(name.rsplit("_", 1)[1])
    calls, original = 0, implementation.frozen_map

    def fail(value):
        nonlocal calls
        calls += 1
        if calls == point:
            raise MemoryError("controlled native harness publication fault")
        return original(value)

    caught = None
    with patch.object(implementation, "frozen_map", side_effect=fail):
        try:
            if name.startswith("fault_define"):
                model.define(Layer.GLYPH, ascii_symbols("new"))
            else:
                budget.apply(model, current, (change(),))
        except MemoryError as exc:
            caught = exc
    check(caught is not None, "fault_not_reached", "controlled fault point was not reached", point=point)
    check(model._state is state and fingerprint(model) == before, "fault_published", "fault published partial state", point=point)
    if name.startswith("fault_define"):
        model.define(Layer.GLYPH, ascii_symbols("new"))
    else:
        recovery = budget.apply(model, current, ())
        check(model.stream(recovery.result_stream_id).root == model.stream(current).root,
              "recovery_wrong", "recovery changed the root")
    return {"point": point, "fault_observed": "MemoryError", "state_unchanged": True, "recovery_passed": True}


def run_probe(name, budget):
    if name.startswith("fault_"):
        return fault_probe(name, budget)
    model, base = make()
    if name == "all_ascii":
        ref = model.define(Layer.DOCUMENT, ascii_symbols(bytes(range(128))))
        stream = model.create_stream(ref)
        data = model.expand_stream(stream.stream_id)
        check(data == bytes(range(128)), "ascii_changed", "base alphabet did not round trip")
        check(ast.literal_eval(model.escaped(stream.stream_id)).encode("ascii") == data, "escape_changed", "escaped inspection lost data")
        check(not any(ord(x) < 32 or ord(x) == 127 for x in model.escaped(stream.stream_id)), "raw_control", "inspection emitted raw control")
    elif name == "meaning_free_literals":
        et = model.define(Layer.GLYPH, ascii_symbols("et"))
        te = model.define(Layer.GLYPH, ascii_symbols("te"))
        plain = model.define(Layer.COMPONENT, (et, te))
        hyphen = model.define(Layer.COMPONENT, (SymbolRef(45), et, te))
        check(model.expand(plain) == b"ette" and model.expand(hyphen) == b"-ette", "literal_changed", "hyphen or glyph assembly changed")
        check(set(model.definition(plain).to_record()) == {"schema_version", "profile", "layer", "children"}, "extra_meaning", "unexpected payload fields")
    elif name == "public_immutability":
        try:
            model.definition(base.root).children = ()
        except FrozenInstanceError:
            pass
        else:
            check(False, "mutable_value", "definition was mutable")
        try:
            model.definitions[base.root.definition_id] = None
        except TypeError:
            pass
        else:
            check(False, "mutable_view", "catalog view was mutable")
    elif name == "detached_records":
        record = model.definition(base.root).to_record()
        record["children"][0]["value"] = 90
        check(model.expand_stream(base.stream_id) == b"abc", "record_alias", "detached record mutated payload")
    elif name == "shared_occurrence":
        word = model.define(Layer.WORD, ascii_symbols("abc"))
        shared = model.create_stream(model.define(Layer.DOCUMENT, (word, word)))
        result = budget.apply(model, shared.stream_id, (Edit("one", "replace", (0,), 0, 1, ascii_symbols("X")),))
        check(model.expand_stream(result.result_stream_id) == b"Xbcabc", "shared_mutation", "edit affected the wrong occurrence")
        check(model.expand(word) == b"abc", "definition_mutated", "shared definition changed")
    elif name == "identity_and_history":
        result = budget.apply(model, base.stream_id, (change("one"), change("two", b"a")))
        check(model.stream(result.result_stream_id).root == base.root, "no_reuse", "return to original did not reuse definition")
        check(len(model.history(result.result_stream_id)) == 3, "lost_occurrence", "restored content erased history")
        check(model.expand_stream(result.output_stream_ids[0]) == b"Xbc", "prefix_changed", "old prefix lost content")
    elif name == "empty_noop":
        empty = model.create_stream(model.define(Layer.DOCUMENT, ()))
        result = budget.apply(model, empty.stream_id, ())
        check(result.result_stream_id != empty.stream_id and model.expand_stream(result.result_stream_id) == b"", "empty_identity", "empty batch lost identity")
    elif name == "request_identity":
        operations = (change(),)
        a = budget.apply(model, base.stream_id, operations)
        b = budget.apply(model, base.stream_id, operations)
        check(a.request_sha256 == b.request_sha256 and a.batch_id != b.batch_id,
              "request_identity", "request content identity confused with occurrence")
    return {"probe": name, "checks_passed": True}


def run_scenario(name, budget, evidence_root):
    if name == "wide_history":
        model, base = make(data=b"A" * 10000)
        current, expected, old = base.stream_id, bytearray(b"A" * 10000), {}
        for n in range(500):
            index, value = n * 17 % 10000, 66 + n % 25
            expected[index] = value
            current = budget.apply(model, current, (Edit(f"op{n}", "replace", (), index, 1, (SymbolRef(value),)),)).result_stream_id
            check(model.expand_stream(current) == bytes(expected), "wide_wrong_bytes", "wide workload disagrees with oracle", step=n)
            if n in (0, 249, 499): old[current] = bytes(expected)
        check(model.expand_stream(base.stream_id) == b"A" * 10000, "wide_original", "wide original changed")
        for stream_id, value in reversed(tuple(old.items())):
            check(model.expand_stream(stream_id) == value, "wide_old", "older stream changed")
        check(len(model.history(current)) == 501, "wide_history", "wide history incomplete")
        return model.stats()
    if name == "deep_shared":
        model = NativeModel()
        ref = model.define(Layer.GLYPH, ascii_symbols("ab"))
        for layer in (Layer.COMPONENT, Layer.ROOT, Layer.WORD, Layer.PHRASE, Layer.SENTENCE, Layer.PARAGRAPH):
            ref = model.define(layer, (ref,))
        base = model.create_stream(model.define(Layer.DOCUMENT, (ref,) * 200))
        current, expected = base.stream_id, bytearray(b"ab" * 200)
        for n in range(32):
            path = (n,) + (0,) * 6
            current = budget.apply(model, current, (Edit(f"deep{n}", "replace", path, 0, 1, ascii_symbols("X")),)).result_stream_id
            expected[n * 2] = 88
            check(model.expand_stream(current) == bytes(expected), "deep_wrong", "deep edit changed a shared occurrence", step=n)
        check(model.expand_stream(base.stream_id) == b"ab" * 200, "deep_original", "deep original changed")
        return {"layers": 8, "shared_occurrences": 200, "edits": 32, "stats": model.stats()}
    if name == "empty_amplification":
        model = NativeModel()
        empty = model.define(Layer.GLYPH, ())
        component = model.define(Layer.COMPONENT, (empty,) * 10000)
        root = model.define(Layer.ROOT, (component,) * 199)
        check(model.expand(root) == b"", "empty_bytes", "empty expansion produced bytes")
        outcome = rejection(model, lambda: model.define(Layer.WORD, (root, root)),
                            {"exception": "NativeError", "code": "LIMIT_EXCEEDED"})
        return {"accepted_traversal_steps": model._state.costs[root.definition_id], **outcome}
    if name == "near_expansion_limit":
        model = NativeModel()
        glyph = model.define(Layer.GLYPH, ascii_symbols("A" * 100))
        component = model.define(Layer.COMPONENT, (glyph,) * 100)
        root = model.define(Layer.ROOT, (component,) * 100)
        check(model.expand(root) == b"A" * 1000000, "expansion_wrong", "one-million-byte expansion changed")
        outcome = rejection(model, lambda: model.define(Layer.WORD, (root, SymbolRef(65))),
                            {"exception": "NativeError", "code": "LIMIT_EXCEEDED"})
        return {"expanded_bytes": 1000000, **outcome}
    if name == "resource_exhaustion":
        outcomes = []
        for n in range(8):
            item = {"input": {"recipe": "resource", "variant": n, "value": n},
                    "expected": {"exception": "NativeError", "code": "LIMIT_EXCEEDED"}}
            outcomes.append(run_error(item, budget))
        return {"resource_boundaries": len(outcomes), "all_rejections_atomic": True}
    if name == "four_callers":
        model, base = make(data=b"A" * 64)
        barrier = threading.Barrier(4)

        def caller(number):
            current, expected = base.stream_id, bytearray(b"A" * 64)
            barrier.wait(timeout=10)
            for n in range(40):
                index, value = (n + number * 7) % 64, 66 + number
                expected[index] = value
                current = budget.apply(model, current, (Edit(f"c{number}-{n}", "replace", (), index, 1, (SymbolRef(value),)),)).result_stream_id
                check(model.expand_stream(current) == bytes(expected), "concurrent_bytes", "caller branch corrupted", caller=number, step=n)
            return current

        with ThreadPoolExecutor(max_workers=4) as pool:
            outputs = list(pool.map(caller, range(4)))
        check(model.stats()["streams"] == 161 and model.stats()["batches"] == 160,
              "concurrent_counts", "concurrent publication lost or duplicated work")
        for stream in outputs:
            check(len(model.history(stream)) == 41, "concurrent_history", "caller ancestry incomplete")
        check(model.expand_stream(base.stream_id) == b"A" * 64, "concurrent_original", "shared base changed")
        ordinals = sorted(int(k.rsplit(":", 1)[1]) for k in model._state.streams)
        check(ordinals == list(range(1, 162)), "concurrent_ids", "stream counters have gaps/duplicates")
        return {"callers": 4, "transformations": 160, "stats": model.stats()}
    if name == "publication_failures":
        outcomes = [fault_probe(f"fault_publish_{n}", budget, pressure=True) for n in range(1, 6)]
        outcomes += [fault_probe(f"fault_define_{n}", budget, pressure=True) for n in range(1, 4)]
        return {"controlled_fault_points": len(outcomes), "all_recovered": True}
    return timeout_probe(evidence_root)


def timeout_probe(evidence_root):
    from ..harness.runner import OwnedProcess
    from .runner import stop_owned
    folder = Path(evidence_root) / "timeout-probe"
    folder.mkdir(exist_ok=False)
    marker = folder / "ready.json"
    started = time.monotonic()
    with (folder / "child.log").open("xb") as log:
        child = OwnedProcess([sys.executable, "-m", "docstream_cpu.native_harness.worker", "--stall-ready", str(marker)], log)
        pid = child.process.pid
        try:
            while not marker.exists() and time.monotonic() - started < 8:
                check(child.process.poll() is None, "timeout_early_exit", "timeout probe child exited before readiness")
                time.sleep(0.02)
            check(marker.exists(), "timeout_not_ready", "timeout probe did not become ready")
            # A supervisor deadline is deliberately shorter than the stalled work.
            time.sleep(0.15)
            check(child.process.poll() is None, "timeout_no_stall", "probe did not remain in flight")
        finally:
            stop_owned(child)
        check(child.process.poll() is not None, "timeout_cleanup", "owned child remained alive")
        result = {"status": "INCOMPLETE", "reason": "controlled supervisor deadline",
                  "owned_pid": pid, "exit_code": child.process.returncode, "owned_child_stopped": True}
        save(folder / "summary.json", result)
    return {"expected_probe_status": "INCOMPLETE", "owned_child_stopped": True,
            "observed_seconds": round(time.monotonic() - started, 3)}


def execute(case, budget, evidence_root):
    family = case["family"]
    if family == "error": return run_error(case, budget)
    if family == "valid": return run_valid(case, budget)
    if family == "probe": return run_probe(case["input"]["name"], budget)
    return run_scenario(case["input"]["name"], budget, evidence_root)
