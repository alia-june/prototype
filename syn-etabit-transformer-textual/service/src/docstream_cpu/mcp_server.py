"""Authenticated loopback MCP adapter. No global client configuration is touched."""
from __future__ import annotations

from functools import partial
import hmac
import secrets
from typing import Any
from urllib.parse import urlsplit

import anyio
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from .errors import ModelError
from .service import CommitRequest, DocumentService, IngestRequest, InspectRequest, TransformRequest
from .storage import Store
from .visual_service import ArtifactRequest, RenderRequest, VisualService
from .format_service import FormatService, ImportRequest, ExportRequest

MAX_BODY = 2 * 1024 * 1024


async def invoke(function, *args):
    try:
        return await anyio.to_thread.run_sync(partial(function, *args))
    except ModelError as exc:
        return {"ok": False, "error": {**exc.to_dict(), "retryable": exc.code == "BUSY", "committed": False}}
    except Exception:
        # Preserve the request key and retry: an exception could follow SQL commit.
        return {"ok": False, "error": {"code": "INTERNAL_ERROR", "message": "request failed; inspect its receipt or retry the identical request", "correlation_id": secrets.token_hex(8), "retryable": True, "committed": "unknown"}}


class LoopbackGuard:
    def __init__(self, app, token: str, close=None):
        if type(token) is not str or len(token) < 32:
            raise ModelError("AUTH_CONFIG", "a bearer token of at least 32 characters is required")
        self.app, self.token = app, token
        self.close = close

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            closed = False

            async def cleanup():
                nonlocal closed
                if not closed and self.close is not None:
                    with anyio.CancelScope(shield=True):
                        await anyio.to_thread.run_sync(self.close)
                    closed = True

            async def lifecycle_send(message):
                if message["type"] in ("lifespan.shutdown.complete", "lifespan.startup.failed"):
                    await cleanup()
                await send(message)

            try:
                return await self.app(scope, receive, lifecycle_send if scope["type"] == "lifespan" else send)
            finally:
                if scope["type"] == "lifespan":
                    await cleanup()
        headers = {}
        for key, value in scope["headers"]:
            name = key.decode("latin-1").lower()
            if name in headers and name in ("host", "origin", "authorization", "content-length"):
                return await self.reject(send, 400)
            headers[name] = value.decode("latin-1")
        host = headers.get("host", "")
        try:
            parsed_host = urlsplit("http://" + host)
            _ = parsed_host.port  # Reject malformed ports rather than ignoring them.
            if parsed_host.hostname not in ("127.0.0.1", "localhost") or parsed_host.username or parsed_host.password or parsed_host.path or parsed_host.query or parsed_host.fragment:
                return await self.reject(send, 403)
            origin = headers.get("origin")
            if origin is not None:
                parsed_origin = urlsplit(origin)
                if parsed_origin.scheme != "http" or parsed_origin.netloc != host or parsed_origin.path or parsed_origin.query or parsed_origin.fragment:
                    return await self.reject(send, 403)
        except ValueError:
            return await self.reject(send, 403)
        supplied = headers.get("authorization", "")
        if not hmac.compare_digest(supplied.encode("utf-8"), ("Bearer " + self.token).encode("utf-8")):
            return await self.reject(send, 401)
        try:
            length = int(headers.get("content-length", "0"))
            if length < 0:
                return await self.reject(send, 400)
            if length > MAX_BODY:
                return await self.reject(send, 413)
        except ValueError:
            return await self.reject(send, 400)
        # Bound chunked bodies too. Do not pass partial oversized JSON to the SDK.
        body = bytearray()
        if scope["method"] == "POST":
            while True:
                try:
                    with anyio.fail_after(10):
                        message = await receive()
                except TimeoutError:
                    return await self.reject(send, 408)
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > MAX_BODY:
                    return await self.reject(send, 413)
                if not message.get("more_body", False):
                    break
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            return await self.app(scope, replay, send)
        return await self.app(scope, receive, send)

    @staticmethod
    async def reject(send, status):
        body = b'{"ok":false,"error":"request rejected"}'
        await send({"type": "http.response.start", "status": status, "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode()), (b"connection", b"close")]})
        await send({"type": "http.response.body", "body": body})


def create_app(store: Store, token: str, renderer=None):
    from starlette.responses import FileResponse, JSONResponse
    from starlette.routing import Route
    service = DocumentService(store)
    visual = VisualService(store, renderer)
    formats = FormatService(store)
    mcp = MCPServer("Docstream", version="0.2.0.dev4", instructions="Use typed batches and durable request keys. Import Markdown or DOCX with an explicit loss policy; inspect structure and transform immutable streams. Render a candidate with commit=true to advance its head after visual output is ready. Exports are separate artifacts.")

    @mcp.tool(structured_output=True)
    async def docstream_status() -> dict[str, Any]:
        """Inspect actual service capabilities; no mutation."""
        return visual.status()

    @mcp.tool(structured_output=True)
    async def docstream_ingest(request: IngestRequest) -> dict[str, Any]:
        """Ingest literal UTF-8 or a structured snapshot with a durable request key."""
        return await invoke(service.ingest, request)

    @mcp.tool(structured_output=True)
    async def docstream_transform(request: TransformRequest) -> dict[str, Any]:
        """Plan, materialize or semantically commit a batch. Use render with a candidate for a rendered commit."""
        return await invoke(service.transform, request)

    @mcp.tool(structured_output=True)
    async def docstream_commit(request: CommitRequest) -> dict[str, Any]:
        """Commit a previously staged candidate's semantic result under head guards."""
        return await invoke(service.commit, request)

    @mcp.tool(structured_output=True)
    async def docstream_inspect(request: InspectRequest) -> dict[str, Any]:
        """Read paginated heads, streams, histories, plans, source metadata or text content."""
        return await invoke(service.inspect, request)

    @mcp.tool(structured_output=True)
    async def docstream_job(job_id: str) -> dict[str, Any]:
        """Inspect a durable request job/receipt, including interrupted requests."""
        return await invoke(service.job, job_id)

    @mcp.tool(structured_output=True)
    async def docstream_render(request: RenderRequest) -> dict[str, Any]:
        """Construct and preview a stream, or render and commit a staged candidate."""
        return await invoke(visual.render, request)

    @mcp.tool(structured_output=True)
    async def docstream_artifact(request: ArtifactRequest) -> dict[str, Any]:
        """Retrieve ready artifact metadata or bounded base64 chunks; download path uses the same bearer token."""
        return await invoke(visual.artifact, request)

    @mcp.tool(structured_output=True)
    async def docstream_import(request: ImportRequest) -> dict[str, Any]:
        """Import Markdown, a Docstream Markdown bundle or DOCX. Original bytes retained; losses reject by default."""
        return await invoke(formats.import_document, request)

    @mcp.tool(structured_output=True)
    async def docstream_export(request: ExportRequest) -> dict[str, Any]:
        """Export a stream to DOCX or a Markdown asset bundle without advancing its head. Losses reject by default."""
        return await invoke(formats.export_document, request)

    async def download(request):
        try:
            path, metadata = await anyio.to_thread.run_sync(visual.artifact_file, request.path_params["artifact_id"])
            return FileResponse(path, media_type=metadata["media_type"], filename=path.name)
        except ModelError:
            return JSONResponse({"ok": False, "error": "artifact unavailable"}, status_code=404)

    security = TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=["127.0.0.1:*", "localhost:*"], allowed_origins=["http://127.0.0.1:*", "http://localhost:*"])
    app = mcp.streamable_http_app(json_response=True, stateless_http=True, max_request_body_size=MAX_BODY, transport_security=security)
    app.routes.insert(0, Route("/artifacts/{artifact_id}", download, methods=["GET"]))
    return LoopbackGuard(app, token, close=visual.close)
