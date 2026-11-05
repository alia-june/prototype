from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .canonical import loads
from .workspace import DurableWorkspace, RecoveryError


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="dwsk", description="Durable Workspace Development Kit")
    sub = p.add_subparsers(dest="cmd", required=True)
    a=sub.add_parser("init"); a.add_argument("root")
    a=sub.add_parser("set"); a.add_argument("root"); a.add_argument("key"); a.add_argument("json_value")
    a=sub.add_parser("get"); a.add_argument("root"); a.add_argument("key")
    a=sub.add_parser("delete"); a.add_argument("root"); a.add_argument("key")
    a=sub.add_parser("verify"); a.add_argument("root")
    a=sub.add_parser("checkpoint"); a.add_argument("root")
    a=sub.add_parser("verify-snapshot"); a.add_argument("snapshot_dir")
    a=sub.add_parser("recover"); a.add_argument("snapshot_dir"); a.add_argument("target_root")
    ns=p.parse_args(argv)
    try:
        if ns.cmd=="init": DurableWorkspace.init(ns.root); print(Path(ns.root).resolve())
        elif ns.cmd=="set": print(json.dumps(DurableWorkspace(ns.root).set(ns.key, loads(ns.json_value)), ensure_ascii=False))
        elif ns.cmd=="get": print(json.dumps(DurableWorkspace(ns.root).get(ns.key), ensure_ascii=False, sort_keys=True))
        elif ns.cmd=="delete": print(json.dumps(DurableWorkspace(ns.root).delete(ns.key), ensure_ascii=False))
        elif ns.cmd=="verify": print(json.dumps(DurableWorkspace(ns.root).verify(), indent=2, sort_keys=True))
        elif ns.cmd=="checkpoint": print(DurableWorkspace(ns.root).checkpoint())
        elif ns.cmd=="verify-snapshot":
            r=DurableWorkspace.inspect_snapshot(ns.snapshot_dir); r.pop("_parsed",None); print(json.dumps(r,indent=2,sort_keys=True))
        elif ns.cmd=="recover": print(DurableWorkspace.recover(ns.snapshot_dir, ns.target_root).root)
        return 0
    except Exception as exc:
        if isinstance(exc, RecoveryError) and exc.details is not None:
            print(json.dumps({"error_type": "RecoveryError", "error": str(exc), "details": exc.details},
                             ensure_ascii=False, sort_keys=True), file=sys.stderr)
            return 2
        print(f"ERROR: {exc}", file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
