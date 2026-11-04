from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from difflib import unified_diff
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading
from typing import Any


_AUDIT_LOCK = threading.Lock()


class DocumentError(Exception):
    """A user-facing document operation error."""


@dataclass(frozen=True)
class EditResult:
    path: str
    replacements: int
    changed: bool
    dry_run: bool
    before_sha256: str
    after_sha256: str
    backup: str | None
    diff: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def append_audit(audit_path: Path, event: dict[str, Any]) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": utc_now(), **event}
    with _AUDIT_LOCK:
        with audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def default_audit_path(target: Path) -> Path:
    return target.parent / ".docstream" / "audit.jsonl"


def compile_flags(flag_names: str) -> int:
    flags = 0
    mapping = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL, "x": re.VERBOSE}
    unknown = sorted(set(flag_names.lower()) - set(mapping))
    if unknown:
        raise DocumentError(f"unsupported regex flags: {''.join(unknown)}")
    for name in flag_names.lower():
        flags |= mapping[name]
    return flags


def regex_edit(
    path: Path,
    pattern: str,
    replacement: str,
    *,
    flags: str = "",
    expected: int | None = None,
    limit: int = 0,
    dry_run: bool = False,
    backup: bool = False,
    audit_path: Path | None = None,
) -> EditResult:
    if not path.is_file():
        raise DocumentError(f"Markdown source does not exist: {path}")
    if len(pattern) > 16_384:
        raise DocumentError("regex pattern exceeds the 16384 character safety limit")
    before = path.read_text(encoding="utf-8")
    before_hash = text_sha256(before)
    try:
        expression = re.compile(pattern, compile_flags(flags))
    except re.error as exc:
        raise DocumentError(f"invalid regex: {exc}") from exc
    after, count = expression.subn(replacement, before, count=max(0, limit))
    if expected is not None and count != expected:
        raise DocumentError(
            f"match-count guard failed: expected {expected}, observed {count}; no file was changed"
        )
    changed = before != after
    preview = "".join(
        unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
    )
    backup_path: Path | None = None
    if changed and not dry_run:
        if backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup_path)
        atomic_write_text(path, after)
    result = EditResult(
        path=str(path.resolve()),
        replacements=count,
        changed=changed,
        dry_run=dry_run,
        before_sha256=before_hash,
        after_sha256=text_sha256(after),
        backup=str(backup_path.resolve()) if backup_path else None,
        diff=preview,
    )
    if not dry_run:
        append_audit(
            audit_path or default_audit_path(path),
            {
                "operation": "regex_edit",
                "target": str(path.resolve()),
                "pattern": pattern,
                "flags": flags,
                "limit": limit,
                "expected": expected,
                "result": {k: v for k, v in result.to_dict().items() if k != "diff"},
            },
        )
    return result


def create_markdown(path: Path, title: str, *, force: bool = False) -> dict[str, Any]:
    if path.exists() and not force:
        raise DocumentError(f"refusing to overwrite existing file: {path}")
    title = title.strip()
    if not title:
        raise DocumentError("title cannot be empty")
    content = f"# {title}\n\n"
    atomic_write_text(path, content)
    result = {"path": str(path.resolve()), "sha256": file_sha256(path), "title": title}
    append_audit(
        default_audit_path(path),
        {"operation": "new", "target": str(path.resolve()), "result": result},
    )
    return result


def inspect_markdown(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DocumentError(f"Markdown source does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings: list[dict[str, Any]] = []
    links = 0
    images = 0
    fenced = False
    code_blocks = 0
    for number, line in enumerate(lines, start=1):
        if line.startswith("```"):
            fenced = not fenced
            if fenced:
                code_blocks += 1
            continue
        if fenced:
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            headings.append(
                {"line": number, "level": len(heading.group(1)), "text": heading.group(2)}
            )
        links += len(re.findall(r"(?<!!)\[[^\]]+\]\([^)]+\)", line))
        images += len(re.findall(r"!\[[^\]]*\]\([^)]+\)", line))
    words = len(re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE))
    return {
        "path": str(path.resolve()),
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
        "lines": len(lines),
        "words": words,
        "headings": headings,
        "links": links,
        "images": images,
        "code_blocks": code_blocks,
        "unclosed_code_fence": fenced,
    }

