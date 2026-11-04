"""Thin MCP client plus explicit foreground service lifecycle."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import socket
import sys
from urllib.parse import urlsplit

from .errors import ModelError


async def client_call(url, token, tool, payload=None, *, mode="auto"):
    import httpx2
    from mcp import Client
    from mcp.client.streamable_http import streamable_http_client

    parsed = urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost") or parsed.username or parsed.password:
        raise ModelError("INVALID_ENDPOINT", "only explicit loopback HTTP endpoints are supported")
    read_budget = 75 if tool == "docstream_render" else 30
    async with httpx2.AsyncClient(headers={"Authorization": "Bearer " + token}, timeout=httpx2.Timeout(10, read=read_budget), trust_env=False) as http:
        transport = streamable_http_client(url, http_client=http)
        async with Client(transport, mode=mode, read_timeout_seconds=read_budget) as client:
            if tool == "list":
                listing = await client.list_tools()
                return {"tools": [item.name for item in listing.tools]}
            arguments = {} if payload is None else ({"job_id": payload["job_id"]} if tool == "docstream_job" else {"request": payload})
            result = await client.call_tool(tool, arguments)
            if result.structured_content is not None:
                return result.structured_content
            return {"is_error": result.is_error, "content": [item.model_dump(mode="json") for item in result.content]}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="docstream-local")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="run the explicitly configured loopback owner in the foreground")
    serve.add_argument("--root", type=Path, required=True)
    serve.add_argument("--port", type=int, default=8765)
    call = sub.add_parser("call", help="send a structured request to an existing service")
    call.add_argument("tool", choices=["list", "docstream_status", "docstream_ingest", "docstream_transform", "docstream_commit", "docstream_inspect", "docstream_job", "docstream_render", "docstream_artifact", "docstream_import", "docstream_export"])
    call.add_argument("--url", default="http://127.0.0.1:8765/mcp")
    call.add_argument("--input", type=Path, help="JSON request file; '-' reads stdin")
    args = parser.parse_args(argv)
    try:
        token = os.environ.get("DOCSTREAM_TOKEN", "")
        if len(token) < 32:
            raise ModelError("AUTH_CONFIG", "set DOCSTREAM_TOKEN to at least 32 characters")
        if args.command == "serve":
            import uvicorn
            from .mcp_server import create_app
            from .storage import Store
            if not 0 <= args.port <= 65535:
                raise ModelError("VALIDATION_ERROR", "invalid port")
            with Store(args.root) as store:
                app = create_app(store, token)
                listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    listener.bind(("127.0.0.1", args.port))
                    port = listener.getsockname()[1]
                    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False, proxy_headers=False, limit_concurrency=32, timeout_graceful_shutdown=5)
                    server = uvicorn.Server(config)
                    print(json.dumps({"endpoint": f"http://127.0.0.1:{port}/mcp", "root": str(store.root)}), flush=True)
                    server.run(sockets=[listener])
                finally:
                    listener.close()
            return 0
        payload = None
        if args.input:
            raw = sys.stdin.read() if str(args.input) == "-" else args.input.read_text(encoding="utf-8")
            payload = json.loads(raw)
        reply = asyncio.run(client_call(args.url, token, args.tool, payload))
        print(json.dumps(reply, ensure_ascii=False, indent=2))
        return 0 if reply.get("ok", not reply.get("is_error", False)) else 2
    except (ModelError, ValueError, OSError) as exc:
        print(json.dumps({"ok": False, "error": {"code": getattr(exc, "code", "CLIENT_ERROR"), "message": str(exc)}}), file=sys.stderr)
        return 2
    except Exception:
        print(json.dumps({"ok": False, "error": {"code": "CONNECTION_ERROR", "message": "service call failed; preserve the request key when retrying"}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
