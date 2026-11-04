from __future__ import annotations

import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request

import uvicorn

from docstream_cpu.cli import client_call
from docstream_cpu.mcp_server import MAX_BODY, create_app
from docstream_cpu.storage import Store

VALIDATION_ROOT = Path(__file__).resolve().parents[2] / ".docstream" / "validation"
VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)


class RunningServer:
    def __init__(self, root, renderer=None):
        self.store = Store(root)
        self.token = secrets.token_hex(32)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 0))
        self.port = self.socket.getsockname()[1]
        self.url = f"http://127.0.0.1:{self.port}/mcp"
        app = create_app(self.store, self.token, renderer=renderer)
        self.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=self.port, log_level="error", access_log=False, proxy_headers=False, timeout_graceful_shutdown=2))
        self.thread = threading.Thread(target=self.server.run, kwargs={"sockets": [self.socket]}, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if not self.thread.is_alive() or time.monotonic() > deadline:
                self.close()
                raise RuntimeError("test service did not start")
            time.sleep(0.02)

    def close(self):
        self.server.should_exit = True
        self.thread.join(10)
        if self.thread.is_alive():
            self.server.force_exit = True
            self.thread.join(5)
        self.socket.close()
        self.store.close()
        if self.thread.is_alive():
            raise RuntimeError("test listener did not stop")


class McpTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(dir=VALIDATION_ROOT)
        self.server = RunningServer(Path(self.folder.name))

    def tearDown(self):
        self.server.close()
        self.folder.cleanup()

    def call(self, name, payload=None, mode="auto"):
        return asyncio.run(client_call(self.server.url, self.server.token, name, payload, mode=mode))

    def test_real_mcp_discovery_and_status(self):
        listing = self.call("list")
        self.assertEqual(set(listing["tools"]), {"docstream_status", "docstream_ingest", "docstream_transform", "docstream_commit", "docstream_inspect", "docstream_job", "docstream_render", "docstream_artifact", "docstream_import", "docstream_export"})
        status = self.call("docstream_status")
        self.assertTrue(status["ok"])
        self.assertEqual(status["visual_state"], "available")

    def test_legacy_protocol_discovery(self):
        self.assertIn("docstream_ingest", self.call("list", mode="legacy")["tools"])

    def test_structured_snapshot_arrays_are_accepted_without_scalar_coercion(self):
        reply = self.call("docstream_ingest", {"request_key": "snapshot", "snapshot": {"blocks": [{"block_id": "a", "text": "Structured"}]}})
        self.assertTrue(reply["ok"], reply)

    def test_structured_agent_workflow_and_two_network_clients(self):
        ingested = self.call("docstream_ingest", {"request_key": "ingest", "text": "Original"})
        self.assertTrue(ingested["ok"], ingested)
        source = ingested["result"]
        def transform(key, value):
            return self.call("docstream_transform", {"request_key": key, "base_stream_id": source["stream_id"], "mode": "commit",
                "batch": {"base_sha256": source["semantic_sha256"], "operations": [{"operation_id": "font", "kind": "set_font", "font_family": value}]}})
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(transform, "one", "B"), pool.submit(transform, "two", "C")]
            results = [future.result(timeout=20) for future in futures]
        self.assertEqual(sum(reply["ok"] for reply in results), 1, results)
        self.assertEqual(next(reply for reply in results if not reply["ok"])["error"]["code"], "STALE_HEAD")
        result = next(reply for reply in results if reply["ok"])
        job = self.call("docstream_job", {"job_id": result["job_id"]})
        self.assertEqual(job["state"], "completed")
        inspected = self.call("docstream_inspect", {"target_id": result["result"]["result_stream_id"], "section": "content"})
        self.assertTrue(inspected["ok"])

    def test_malformed_request_rejected_by_schema(self):
        result = self.call("docstream_ingest", {"request_key": "bad", "text": "x", "title": False})
        self.assertTrue(result.get("is_error") or result.get("ok") is False, result)

    def http_status(self, headers, body=b"{}"):
        request = urllib.request.Request(self.server.url, data=body, headers={"Content-Type": "application/json", **headers})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status
        except urllib.error.HTTPError as error:
            error.close()
            return error.code

    def test_auth_origin_host_and_body_limits(self):
        self.assertEqual(self.http_status({}), 401)
        self.assertEqual(self.http_status({"Authorization": "Bearer wrong"}), 401)
        auth = {"Authorization": "Bearer " + self.server.token}
        self.assertEqual(self.http_status({**auth, "Origin": "https://external.invalid"}), 403)
        self.assertEqual(self.http_status({**auth, "Host": "external.invalid"}), 403)
        # Send oversized declared length before uploading a body; eager rejection
        # of an already-uploading huge body can appear as a Windows TCP reset.
        with socket.create_connection(("127.0.0.1", self.server.port), timeout=5) as connection:
            headers = (f"POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{self.server.port}\r\n"
                       f"Authorization: Bearer {self.server.token}\r\nContent-Type: application/json\r\n"
                       f"Content-Length: {MAX_BODY + 1}\r\nConnection: close\r\n\r\n")
            connection.sendall(headers.encode())
            self.assertIn(b"413", connection.recv(4096).split(b"\r\n", 1)[0])

    def test_chunked_body_limit_is_enforced_without_content_length(self):
        app = create_app(self.server.store, self.server.token)
        messages = iter([{"type": "http.request", "body": b"x" * (MAX_BODY + 1), "more_body": False}])
        replies = []
        scope = {"type": "http", "method": "POST", "headers": [(b"host", b"127.0.0.1"), (b"authorization", ("Bearer " + self.server.token).encode())]}
        async def receive():
            return next(messages)
        async def send(message):
            replies.append(message)
        asyncio.run(app(scope, receive, send))
        self.assertEqual(replies[0]["status"], 413)

    def test_thin_cli_uses_same_service(self):
        environment = dict(os.environ)
        environment["DOCSTREAM_TOKEN"] = self.server.token
        process = subprocess.run([sys.executable, "-m", "docstream_cpu", "call", "docstream_status", "--url", self.server.url],
            env=environment, capture_output=True, text=True, timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue(json.loads(process.stdout)["ok"])
        self.assertNotIn(self.server.token, process.stdout + process.stderr)

    def test_no_listener_remains_after_shutdown(self):
        port = self.server.port
        self.server.close()
        with socket.socket() as probe:
            self.assertNotEqual(probe.connect_ex(("127.0.0.1", port)), 0)
        # Replace with a fresh instance so teardown exercises an ordinary shutdown too.
        self.server = RunningServer(Path(self.folder.name))

    def test_foreground_cli_service_restart_replays_network_receipt(self):
        root = Path(self.folder.name) / "cli-service"
        environment = dict(os.environ)
        environment["DOCSTREAM_TOKEN"] = self.server.token
        replies = []
        for _ in range(2):
            process = subprocess.Popen([sys.executable, "-m", "docstream_cpu", "serve", "--root", str(root), "--port", "0"],
                env=environment, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            lines = queue.Queue()
            reader = threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True)
            reader.start()
            port = None
            try:
                endpoint = json.loads(lines.get(timeout=15))["endpoint"]
                port = int(endpoint.split(":")[-1].split("/")[0])
                deadline = time.monotonic() + 10
                while True:
                    try:
                        reply = asyncio.run(client_call(endpoint, self.server.token, "docstream_ingest", {"request_key": "durable-cli", "text": "Survives process restart"}))
                        replies.append(reply)
                        break
                    except Exception:
                        if time.monotonic() > deadline:
                            raise
                        time.sleep(0.05)
            finally:
                process.terminate()
                process.wait(timeout=10)
                process.stdout.close()
                reader.join(1)
                if port is not None:
                    # Windows may finish closing Winsock state just after the
                    # process handle becomes signaled. Bound the shutdown wait.
                    deadline = time.monotonic() + 5
                    while True:
                        with socket.socket() as probe:
                            probe.settimeout(0.2)
                            stopped = probe.connect_ex(("127.0.0.1", port)) != 0
                        if stopped or time.monotonic() >= deadline:
                            break
                        time.sleep(0.05)
                    self.assertTrue(stopped, "foreground test listener did not stop")
        self.assertEqual(replies[0], replies[1])
        self.assertTrue(replies[0]["ok"], replies)


if __name__ == "__main__":
    unittest.main()
