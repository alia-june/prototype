import test from "node:test";
import assert from "node:assert/strict";
import { MathSC0ControlPlane } from "../src/control-plane.mjs";
import { probePythonCapabilities, benchmarkPythonBackends } from "../src/python-worker.mjs";

const failedLocal = async () => ({ status: "failed", error: "unsupported", trace: [] });

test("real Python data plane computes exact rational before fallbacks", async () => {
  const calls = [];
  const cp = new MathSC0ControlPlane({
    webProvider: async () => { calls.push("web"); return 42; },
    llmProvider: async () => { calls.push("llm"); return 99; },
  });
  const r = await cp.compute({ operation: "div", operands: ["1", "3"], mode: "exact" });
  assert.equal(r.backend, "exact");
  assert.equal(r.status, "verified");
  assert.deepEqual(r.value, { $type: "fraction", numerator: 1, denominator: 3 });
  assert.deepEqual(calls, []);
});

test("web is used before LLM", async () => {
  const calls = [];
  const cp = new MathSC0ControlPlane({
    localRunner: failedLocal,
    webProvider: async () => { calls.push("web"); return 42; },
    llmProvider: async () => { calls.push("llm"); return 99; },
  });
  const r = await cp.compute({ operation: "unknown", operands: [] });
  assert.equal(r.backend, "web");
  assert.equal(r.status, "web_sourced");
  assert.equal(r.verified, false);
  assert.deepEqual(calls, ["web"]);
});

test("LLM is strict last resort and cannot self-verify", async () => {
  const calls = [];
  const cp = new MathSC0ControlPlane({
    localRunner: failedLocal,
    webProvider: async () => { calls.push("web"); throw new Error("offline"); },
    llmProvider: async () => {
      calls.push("llm");
      return { value: "heuristic", verified: true, status: "verified" };
    },
  });
  const r = await cp.compute({ operation: "unknown", operands: [] });
  assert.deepEqual(calls, ["web", "llm"]);
  assert.equal(r.backend, "llm_fallback");
  assert.equal(r.status, "llm_inferred");
  assert.equal(r.verified, false);
  assert.equal(r.authority, "heuristic");
});

test("disabled external fallbacks produce failure", async () => {
  const cp = new MathSC0ControlPlane({ localRunner: failedLocal, webProvider: async () => 1, llmProvider: async () => 2 });
  const r = await cp.compute({ operation: "unknown", operands: [], allow_web: false, allow_llm: false });
  assert.equal(r.status, "failed");
  assert.equal(r.backend, "none");
});

test("real JavaScript -> Python -> C/C++ path dispatches native kernel", async () => {
  const cp = new MathSC0ControlPlane();
  const values = Array.from({ length: 100 }, (_, i) => i + 1);
  const r = await cp.compute({ operation: "sum", operands: [values], mode: "float64" });
  assert.equal(r.backend, "native");
  assert.equal(r.value, 5050);
  assert.equal(r.status, "verified");
  assert.equal(r.verified, true);
  assert.match(r.metadata.native_version, /native-0\.8\.0/);
});

test("operation contract rejects malformed known request before local or web dispatch", async () => {
  const calls = [];
  const cp = new MathSC0ControlPlane({
    localRunner: async () => { calls.push("local"); return { status: "failed" }; },
    webProvider: async () => { calls.push("web"); return 1; },
  });
  await assert.rejects(
    cp.compute({ operation: "add", operands: [[1, 2], [3]], mode: "float64" }),
    /identical shapes/
  );
  assert.deepEqual(calls, []);
});

test("versioned operation id resolves and crosses JS -> Python boundary", async () => {
  const cp = new MathSC0ControlPlane();
  const r = await cp.compute({ operation: "math.sc0.add.v1", operands: [7, 8], mode: "exact" });
  assert.equal(r.status, "verified");
  assert.deepEqual(r.value, { $type: "fraction", numerator: 15, denominator: 1 });
  assert.equal(r.metadata.operation_id, "math.sc0.add.v1");
  assert.equal(r.metadata.contract_version, "0.6.0");
});

test("unknown operation preserves web then LLM fallback as uncontracted", async () => {
  const calls = [];
  const cp = new MathSC0ControlPlane({
    webProvider: async () => { calls.push("web"); return 123; },
    llmProvider: async () => { calls.push("llm"); return 456; },
  });
  const r = await cp.compute({ operation: "future_operation", operands: [1] });
  assert.equal(r.backend, "web");
  assert.deepEqual(calls, ["web"]);
  assert.equal(r.metadata.contract_state, "uncontracted");
});

test("contract rejects NaN and invalid log base", async () => {
  const cp = new MathSC0ControlPlane({ localRunner: failedLocal });
  await assert.rejects(cp.compute({ operation: "sqrt", operands: [Number.NaN], mode: "float64" }), /non-finite/);
  await assert.rejects(cp.compute({ operation: "log", operands: [8, 1], mode: "float64" }), /log base/);
});

test("exact pow contract rejects a non-integer exponent", async () => {
  const cp = new MathSC0ControlPlane();
  await assert.rejects(cp.compute({ operation: "pow", operands: ["4", "1/2"], mode: "exact" }), /integer/);
});


test("deterministic result exposes numerical evidence through JS boundary", async () => {
  const cp = new MathSC0ControlPlane();
  const r = await cp.compute({ operation: "sum", operands: [[0.1, 0.2, 0.3]], mode: "float64" });
  assert.equal(r.metadata.numerical_assessment.error_bound.kind, "forward_error_model");
  assert.equal(r.metadata.numerical_assessment.error_bound.rigor, "model_based");
});

test("JavaScript can probe versioned Python backend capabilities", async () => {
  const state = await probePythonCapabilities();
  assert.equal(state.capability_protocol_version, "0.3.0");
  assert.ok(state.backends.some((x) => x.name === "cpu" && x.available === true));
});


test("interval request crosses JS -> Python and preserves exact enclosure endpoints", async () => {
  const cp = new MathSC0ControlPlane();
  const r = await cp.compute({
    operation: "add",
    operands: [
      { $type: "interval", lo: "1/10", hi: "1/5" },
      { $type: "interval", lo: "1/3", hi: "1/2" },
    ],
    mode: "interval",
  });
  assert.equal(r.backend, "interval");
  assert.equal(r.status, "verified");
  assert.deepEqual(r.value.lo, { $type: "fraction", numerator: 13, denominator: 30 });
  assert.deepEqual(r.value.hi, { $type: "fraction", numerator: 7, denominator: 10 });
  assert.equal(r.metadata.numerical_assessment.error_bound.rigor, "rigorous");
});

test("interval division containing zero is rejected at JavaScript contract gate", async () => {
  const cp = new MathSC0ControlPlane();
  await assert.rejects(
    cp.compute({ operation: "div", operands: [1, { $type: "interval", lo: -1, hi: 1 }], mode: "interval" }),
    /contain zero/
  );
});

test("Python benchmark control returns host-specific informational calibration", async () => {
  const profile = await benchmarkPythonBackends({ repeats: 1, sizes: [64] });
  assert.equal(profile.benchmark_version, "0.1.0");
  assert.equal(profile.host_specific, true);
  assert.equal(profile.policy_effect, "informational_only");
  assert.equal(profile.workloads[0].size, 64);
});

test("JavaScript -> Python -> native LU solve path", async () => {
  const cp = new MathSC0ControlPlane();
  const n = 8;
  const A = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => i === j ? 5 : (Math.abs(i-j) === 1 ? 0.25 : 0)));
  const b = Array.from({ length: n }, (_, i) => i + 1);
  const r = await cp.compute({ operation: "solve", operands: [A, b], mode: "float64", tolerance: 1e-10 });
  assert.equal(r.status, "verified");
  assert.equal(r.backend, "native");
  assert.match(r.metadata.native_version, /native-0\.8\.0/);
  assert.ok(r.metadata.verification_residual_inf <= r.metadata.verification_threshold);
});

test("JavaScript -> Python directed-rounding interval transcendental path", async () => {
  const cp = new MathSC0ControlPlane();
  const r = await cp.compute({
    operation: "sqrt",
    operands: [{ $type: "interval", lo: "2", hi: "2" }],
    mode: "interval",
    precision: 80,
  });
  assert.equal(r.status, "verified");
  assert.equal(r.backend, "interval");
  assert.equal(r.metadata.enclosure_rigor, "directed_rounding_backend_enclosure");
  assert.equal(r.metadata.numerical_assessment.error_bound.rigor, "backend_directed_rounding");
});
