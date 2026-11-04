"""Command-line inspection of the hash-pinned AUTH-18B packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from . import TheoryInspectionError, TheoryInspector


def _render_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(f"{row.get('id', '-')}: {row.get('term', row.get('title', row.get('kind', '')))}"
                         for row in value)
    if isinstance(value, dict):
        return "\n".join(f"{key}: {json.dumps(item, ensure_ascii=True, sort_keys=True) if isinstance(item, (dict, list)) else item}"
                         for key, item in value.items())
    return str(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect the read-only AUTH-18B source study")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("summary", "validate", "gaps", "conflicts"):
        sub.add_parser(name)
    for name in ("sources", "relations", "crosswalk", "sample"):
        query = sub.add_parser(name)
        query.add_argument("--query")
        query.add_argument("--status")
        query.add_argument("--domain")
        query.add_argument("--source")
        query.add_argument("--limit", type=int)
    for name in ("source", "relation", "crosswalk-entry"):
        one = sub.add_parser(name)
        one.add_argument("id")
    trace = sub.add_parser("trace")
    trace.add_argument("id")
    trace.add_argument("--depth", type=int, default=4)
    args = parser.parse_args(argv)
    try:
        inspector = TheoryInspector(args.root)
        if args.command == "summary":
            result = inspector.summary()
        elif args.command == "validate":
            result = inspector.validate()
        elif args.command in ("source", "relation", "crosswalk-entry"):
            result = inspector.one(args.id)
        elif args.command == "trace":
            result = inspector.trace(args.id, args.depth)
        elif args.command in ("gaps", "conflicts"):
            result = getattr(inspector, args.command)()
        else:
            filters = {key: getattr(args, key) for key in ("query", "status", "domain", "source", "limit")}
            result = getattr(inspector, args.command)(**filters)
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True)
              if args.format == "json" else _render_text(result))
        return 0
    except (TheoryInspectionError, OSError) as exc:
        error = {"status": "ERROR", "code": getattr(exc, "code", "INSPECTION_ERROR"),
                 "message": str(exc)}
        print(json.dumps(error, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
