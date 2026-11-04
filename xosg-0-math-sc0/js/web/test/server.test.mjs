import test from "node:test";
import assert from "node:assert/strict";
import { createAppServer } from "../server.mjs";

async function withServer(fn, controlPlane = undefined) {
  const server = createAppServer(controlPlane ? { controlPlane } : {});
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  try { await fn(`http://127.0.0.1:${port}`); }
  finally { await new Promise((resolve) => server.close(resolve)); }
}

test("health endpoint", async () => {
  await withServer(async (base) => {
    const r = await fetch(`${base}/api/health`);
    assert.equal(r.status, 200);
    const body = await r.json();
    assert.equal(body.status, "ok");
    assert.equal(body.ui_version, "0.5.0");
  });
});

test("contracts endpoint exposes operation contracts", async () => {
  await withServer(async (base) => {
    const r = await fetch(`${base}/api/contracts`);
    const body = await r.json();
    assert.equal(body.contract_version, "0.6.0");
    assert.equal(body.operations.add.operation_id, "math.sc0.add.v1");
  });
});

test("compute endpoint reaches deterministic control plane", async () => {
  await withServer(async (base) => {
    const r = await fetch(`${base}/api/compute`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ operation: "add", operands: [20, 22], mode: "auto", allow_web: false, allow_llm: false }),
    });
    assert.equal(r.status, 200);
    const body = await r.json();
    assert.deepEqual(body.value, { $type: "fraction", numerator: 42, denominator: 1 });
    assert.equal(body.verified, true);
    assert.equal(body.control_plane, "javascript");
  });
});

test("failed control-plane result maps to HTTP 422", async () => {
  const controlPlane = { compute: async () => ({ status: "failed", value: null, verified: false, backend: "none" }) };
  await withServer(async (base) => {
    const r = await fetch(`${base}/api/compute`, { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
    assert.equal(r.status, 422);
  }, controlPlane);
});

test("static UI is served with restrictive CSP", async () => {
  await withServer(async (base) => {
    const r = await fetch(`${base}/`);
    assert.equal(r.status, 200);
    assert.match(r.headers.get("content-security-policy"), /default-src 'self'/);
    const text = await r.text();
    assert.match(text, /MATH\.SC-0/);
    assert.match(text, /app\.mjs/);
  });
});


test("contract-invalid compute request returns 422 without becoming server failure", async () => {
  await withServer(async (base) => {
    const r = await fetch(`${base}/api/compute`, {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ operation: "add", operands: [[1, 2], [3]], mode: "float64" }),
    });
    assert.equal(r.status, 422);
    const body = await r.json();
    assert.equal(body.status, "failed");
    assert.match(body.error, /ContractError/);
  });
});
