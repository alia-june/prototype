#!/usr/bin/env python3
"""Seeded fuzzing and contention torture for the Mill single-tool controller."""
from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import os
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROLLER_ROOT = HERE.parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SOURCE_ROOT = Path(os.environ.get("MILL_FACTORY_ROOT", REPOSITORY_ROOT / "mill-factory"))
SPEC = importlib.util.spec_from_file_location("mill_controller", CONTROLLER_ROOT / "controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(controller)

SEED = 2026110501
FUZZ_CASES = 1000
CONTENTION_ROUNDS = 20
CONTENTION_WORKERS = 32


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def base_request(root: Path, request_id: str, slug: str) -> dict:
    return {
        "request_id": request_id,
        "slug": slug,
        "title": "Harness batch",
        "scope": "Controller hardening validation.",
        "date": "2026-11-05",
        "workspace_root": str(root),
        "output_root": str(root / "controller-output"),
        "owner": "hardening-harness",
    }


def authority(request: dict, identity: dict, root: Path) -> dict:
    return {
        "authority_id": "harness-authority",
        "authorized_by": "approved-hardening-harness",
        "request_digest": controller.request_digest(request),
        "tool_identity_sha256": identity["sha256"],
        "allowed_output_roots": [str(root / "controller-output")],
    }


def fuzz_request(request: dict, rng: random.Random, root: Path) -> None:
    field = rng.choice(["slug", "title", "scope", "date", "workspace_root", "output_root", "owner", "omit"])
    if field == "slug":
        request[field] = rng.choice(["bad_slug", "-leading", "two--hyphens", "OK", "ok-2", "\x00bad", ""])
    elif field == "title":
        request[field] = rng.choice(["", " ", "valid title", "nul\x00title", 7, None])
    elif field == "scope":
        request[field] = rng.choice(["", " ", "valid scope", "nul\x00scope", 9, None])
    elif field == "date":
        request[field] = rng.choice(["2026-02-30", "2026-2-3", "not-a-date", "2026-11-05", "\x00", None])
    elif field == "workspace_root":
        request[field] = rng.choice([str(root), str(root / "other"), "", "\x00", 1, None])
    elif field == "output_root":
        request[field] = rng.choice([str(root / "controller-output"), str(root / "outside"), "", " ", "\x00", 2, None])
    elif field == "owner":
        request[field] = rng.choice(["owner", "\x00owner", "", None, 5])
    else:
        request.pop(rng.choice(["slug", "title", "scope", "date", "workspace_root"]), None)


def run_fuzz(run_root: Path, identity: dict) -> dict:
    rng = random.Random(SEED)
    records: list[dict] = []
    results = Counter()
    fuzz_root = run_root / "fuzz-workspace"
    state_root = run_root / "fuzz-state"
    for index in range(FUZZ_CASES):
        request = base_request(fuzz_root, f"fuzz-{index:04d}", "fuzz-case")
        fuzz_request(request, rng, fuzz_root)
        current_authority = authority(request, identity, fuzz_root)
        receipt = controller.execute(request, current_authority, SOURCE_ROOT, state_root, "pwsh", admit_only=True)
        if (fuzz_root / "controller-output").exists():
            raise AssertionError("admission-only fuzzing created a Mill output root")
        results[(receipt["admission"], receipt["next_permitted_action"])] += 1
        records.append({"index": index, "request": request, "receipt": {
            key: receipt[key] for key in ("admission", "next_permitted_action", "problems", "retained_state")
        }})
    with (run_root / "fuzz-cases.jsonl").open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, sort_keys=True) + "\n")
    return {"seed": SEED, "cases": FUZZ_CASES, "outcomes": {f"{key[0]}:{key[1]}": value for key, value in results.items()},
            "mill_output_created": False}


def run_contention_round(run_root: Path, identity: dict, round_index: int) -> dict:
    root = run_root / "torture" / f"round-{round_index:02d}"
    state = root / "state"
    shared_slug = f"contention-{round_index:02d}"

    def submit(worker: int) -> dict:
        request = base_request(root, f"round-{round_index:02d}-worker-{worker:02d}", shared_slug)
        return controller.execute(request, authority(request, identity, root), SOURCE_ROOT, state, "pwsh")

    with concurrent.futures.ThreadPoolExecutor(max_workers=CONTENTION_WORKERS) as pool:
        receipts = list(pool.map(submit, range(CONTENTION_WORKERS)))
    created = [receipt for receipt in receipts if receipt["artifact_verification"] == "pass"]
    if len(created) != 1:
        raise AssertionError(f"round {round_index}: expected one verified creation, got {len(created)}")
    batch_path = Path(created[0]["derived"]["batch_path"])
    if not batch_path.is_dir():
        raise AssertionError(f"round {round_index}: verified batch does not exist")
    normal_receipts = list((state / "receipts").glob("*.json"))
    emergency_receipts = list((state / "emergency-receipts").glob("*.json"))
    if len(normal_receipts) != CONTENTION_WORKERS or emergency_receipts:
        raise AssertionError(
            f"round {round_index}: expected {CONTENTION_WORKERS} normal receipts and no emergency receipts; "
            f"got {len(normal_receipts)} normal and {len(emergency_receipts)} emergency"
        )
    outcomes = Counter(receipt["next_permitted_action"] for receipt in receipts)
    return {"round": round_index, "workers": CONTENTION_WORKERS, "verified_creations": len(created),
            "batch_path": str(batch_path), "next_actions": dict(outcomes)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True, type=Path)
    arguments = parser.parse_args()
    run_root = arguments.run_root.resolve()
    predeclared_logs = {"harness.stdout.txt", "harness.stderr.txt"}
    unexpected = [path for path in run_root.iterdir()] if run_root.exists() else []
    unexpected = [path for path in unexpected if path.name not in predeclared_logs]
    if unexpected:
        raise SystemExit(f"Run root must be absent or empty: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    identity = controller.tree_identity(SOURCE_ROOT)
    fuzz = run_fuzz(run_root, identity)
    rounds = [run_contention_round(run_root, identity, index) for index in range(CONTENTION_ROUNDS)]
    summary = {"harness": "mill-single-tool-controller", "seed": SEED, "fuzz": fuzz,
               "contention": {"rounds": CONTENTION_ROUNDS, "workers_per_round": CONTENTION_WORKERS,
                              "round_results": rounds}, "tool_identity": identity}
    write_json(run_root / "HARNESS_SUMMARY.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
