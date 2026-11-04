from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from . import __version__
from .conversion import import_docx, publish_docx
from .core import DocumentError, create_markdown, inspect_markdown, regex_edit
from .service import run_server


def emit(payload: Any, *, as_json: bool = False) -> None:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif isinstance(payload, dict):
        for key, value in payload.items():
            if key == "diff" and value:
                print(value, end="" if value.endswith("\n") else "\n")
            else:
                print(f"{key}: {value}")
    else:
        print(payload)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="docstream",
        description="Edit Markdown canonically and import or publish DOCX documents.",
    )
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)

    new = commands.add_parser("new", help="create a Markdown document")
    new.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    new.add_argument("path", type=Path)
    new.add_argument("--title", required=True)
    new.add_argument("--force", action="store_true")

    inspect = commands.add_parser("inspect", help="inspect Markdown structure")
    inspect.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    inspect.add_argument("path", type=Path)

    edit = commands.add_parser("edit", help="perform a guarded regex replacement")
    edit.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    edit.add_argument("path", type=Path)
    edit.add_argument("--pattern", required=True)
    edit.add_argument("--replacement", default="")
    edit.add_argument("--flags", default="", help="regex flags: i, m, s, x")
    edit.add_argument("--expected", type=int, help="require this exact match count")
    edit.add_argument("--limit", type=int, default=0, help="maximum replacements; 0 means all")
    edit.add_argument("--dry-run", action="store_true")
    edit.add_argument("--backup", action="store_true")

    importing = commands.add_parser("import", help="convert DOCX to Markdown")
    importing.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    importing.add_argument("source", type=Path)
    importing.add_argument("--output", "-o", required=True, type=Path)
    importing.add_argument("--backend", choices=["auto", "pandoc", "native"], default="auto")
    importing.add_argument("--pandoc", help="Pandoc executable or absolute path")
    importing.add_argument("--force", action="store_true")

    publish = commands.add_parser("publish", help="convert Markdown to DOCX")
    publish.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    publish.add_argument("source", type=Path)
    publish.add_argument("--output", "-o", required=True, type=Path)
    publish.add_argument("--backend", choices=["auto", "pandoc", "native"], default="auto")
    publish.add_argument("--pandoc", help="Pandoc executable or absolute path")
    publish.add_argument("--reference-doc", type=Path)
    publish.add_argument("--force", action="store_true")

    serve = commands.add_parser("serve", help="start the root-scoped local JSON service")
    serve.set_defaults(json=False)
    serve.add_argument("--root", type=Path, required=True)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--backend", choices=["auto", "pandoc", "native"], default="auto")
    serve.add_argument("--pandoc", help="Pandoc executable or absolute path")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "new":
            result = create_markdown(args.path, args.title, force=args.force)
        elif args.command == "inspect":
            result = inspect_markdown(args.path)
        elif args.command == "edit":
            result = regex_edit(
                args.path,
                args.pattern,
                args.replacement,
                flags=args.flags,
                expected=args.expected,
                limit=args.limit,
                dry_run=args.dry_run,
                backup=args.backup,
            )
        elif args.command == "import":
            result = import_docx(
                args.source,
                args.output,
                backend=args.backend,
                pandoc=args.pandoc,
                force=args.force,
            )
        elif args.command == "publish":
            result = publish_docx(
                args.source,
                args.output,
                backend=args.backend,
                pandoc=args.pandoc,
                reference_doc=args.reference_doc,
                force=args.force,
            )
        elif args.command == "serve":
            run_server(
                args.root,
                args.host,
                args.port,
                backend=args.backend,
                pandoc=args.pandoc,
            )
            return 0
        else:
            raise DocumentError(f"unknown command: {args.command}")
        emit(result, as_json=args.json)
        return 0
    except DocumentError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

