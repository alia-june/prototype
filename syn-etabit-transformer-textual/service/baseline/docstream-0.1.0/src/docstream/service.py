from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from typing import Any
from urllib.parse import urlparse

from . import __version__
from .conversion import import_docx, publish_docx
from .core import DocumentError, create_markdown, inspect_markdown, regex_edit


class DocumentService:
    def __init__(self, root: Path, *, backend: str = "auto", pandoc: str | None = None):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.backend = backend
        self.pandoc = pandoc
        self._mutation_lock = threading.RLock()

    def resolve(self, supplied: str) -> Path:
        candidate = (self.root / supplied).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise DocumentError("path escapes the configured service root") from exc
        return candidate

    def execute(self, route: str, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        if route == "/v1/health":
            return 200, {"ok": True, "version": __version__, "root": str(self.root)}
        if route == "/v1/new":
            with self._mutation_lock:
                result = create_markdown(
                    self.resolve(body["path"]), body["title"], force=bool(body.get("force"))
                )
            return 201, result
        if route == "/v1/inspect":
            return 200, inspect_markdown(self.resolve(body["path"]))
        if route == "/v1/edit":
            with self._mutation_lock:
                result = regex_edit(
                    self.resolve(body["path"]),
                    body["pattern"],
                    body.get("replacement", ""),
                    flags=body.get("flags", ""),
                    expected=body.get("expected"),
                    limit=int(body.get("limit", 0)),
                    dry_run=bool(body.get("dry_run")),
                    backup=bool(body.get("backup")),
                    audit_path=self.root / ".docstream" / "audit.jsonl",
                )
            return 200, result.to_dict()
        if route == "/v1/import":
            with self._mutation_lock:
                result = import_docx(
                    self.resolve(body["source"]),
                    self.resolve(body["output"]),
                    backend=body.get("backend", self.backend),
                    pandoc=body.get("pandoc", self.pandoc),
                    force=bool(body.get("force")),
                    audit_path=self.root / ".docstream" / "audit.jsonl",
                )
            return 201, result.to_dict()
        if route == "/v1/publish":
            reference = body.get("reference_doc")
            with self._mutation_lock:
                result = publish_docx(
                    self.resolve(body["source"]),
                    self.resolve(body["output"]),
                    backend=body.get("backend", self.backend),
                    pandoc=body.get("pandoc", self.pandoc),
                    reference_doc=self.resolve(reference) if reference else None,
                    force=bool(body.get("force")),
                    audit_path=self.root / ".docstream" / "audit.jsonl",
                )
            return 201, result.to_dict()
        raise DocumentError(f"unknown endpoint: {route}")


def make_handler(service: DocumentService) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = f"Docstream/{__version__}"

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/v1/health":
                self._send(404, {"ok": False, "error": "not found"})
                return
            status, payload = service.execute("/v1/health", {})
            self._send(status, payload)

        def do_POST(self) -> None:  # noqa: N802
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length > 2 * 1024 * 1024:
                    raise DocumentError("request body exceeds 2 MiB")
                raw = self.rfile.read(length)
                body = json.loads(raw.decode("utf-8")) if raw else {}
                if not isinstance(body, dict):
                    raise DocumentError("JSON body must be an object")
                status, payload = service.execute(urlparse(self.path).path, body)
                self._send(status, {"ok": True, "result": payload})
            except KeyError as exc:
                self._send(400, {"ok": False, "error": f"missing field: {exc.args[0]}"})
            except (DocumentError, ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self._send(500, {"ok": False, "error": f"internal error: {exc}"})

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"{self.address_string()} - {fmt % args}")

    return Handler


def run_server(
    root: Path,
    host: str,
    port: int,
    *,
    backend: str = "auto",
    pandoc: str | None = None,
) -> None:
    service = DocumentService(root, backend=backend, pandoc=pandoc)
    server = ThreadingHTTPServer((host, port), make_handler(service))
    print(f"Docstream {__version__} listening on http://{host}:{port} root={service.root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

