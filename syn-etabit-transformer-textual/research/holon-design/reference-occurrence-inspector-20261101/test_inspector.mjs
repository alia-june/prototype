import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const require = createRequire(import.meta.url);
require("./data.js");
const core = require("./inspector-core.js");
const packet = globalThis.REFERENCE_OCCURRENCE_INSPECTOR_DATA;
const here = path.dirname(fileURLToPath(import.meta.url));

const clone = value => core.deepClone(value);
const hashBytes = bytes => createHash("sha256").update(bytes).digest("hex");
const find = (records, id) => records.find(record => record.id === id);

async function rehash(target) {
  target.payload_sha256 = await core.sha256Hex(core.canonicalStringify(target.payload));
}

test("rigid: display packet records the exact untouched source bytes", async () => {
  for (const source of packet.source_files) {
    const absolute = path.resolve(here, source.path);
    const bytes = await readFile(absolute);
    assert.equal(bytes.length, source.bytes, source.path);
    assert.equal(hashBytes(bytes), source.sha256, source.path);
  }
});

test("rigid: accepted snapshot has zero findings and verified digests", async () => {
  const analysis = await core.analyzePacket(packet);
  assert.equal(analysis.status, "valid");
  assert.deepEqual(analysis.findings, []);
  assert.equal(analysis.digestResults.size, 3);
  for (const result of analysis.digestResults.values()) assert.equal(result.status, "verified");
});

test("rigid: record-family counts are exact", () => {
  assert.deepEqual(
    Object.fromEntries(Object.entries(core.COLLECTION_BY_KIND).map(([kind, collection]) => [kind, packet.fixture[collection].length])),
    { target: 3, relationship: 1, metadata: 1, occurrence: 3, view: 2 }
  );
});

test("rigid: chronological and reverse orders are exact", () => {
  const v0 = core.resolveView(packet.fixture, "view:V0");
  const v1 = core.resolveView(packet.fixture, "view:V1");
  assert.deepEqual(v0.entries.map(entry => entry.occurrenceId), ["occurrence:O0", "occurrence:O1", "occurrence:O2"]);
  assert.deepEqual(v1.entries.map(entry => entry.occurrenceId), ["occurrence:O2", "occurrence:O1", "occurrence:O0"]);
});

test("rigid: comparison changes order without changing identity or history", () => {
  const comparison = core.compareViews(packet.fixture, "view:V0", "view:V1");
  assert.equal(comparison.sameOccurrenceSet, true);
  assert.equal(comparison.sameOrder, false);
  assert.equal(comparison.historyMutated, false);
  assert.equal(comparison.rollbackPerformed, false);
});

test("rigid: every occurrence resolves target, relationship and metadata", () => {
  const resolved = core.resolveView(packet.fixture, "view:V0");
  for (const entry of resolved.entries) {
    assert.ok(entry.occurrence, entry.occurrenceId);
    assert.ok(entry.target, entry.occurrenceId);
    assert.ok(entry.relationship, entry.occurrenceId);
    assert.ok(entry.metadata, entry.occurrenceId);
  }
});

test("rigid: canonical payload digests match all three source values", async () => {
  for (const target of packet.fixture.targets) {
    const actual = await core.sha256Hex(core.canonicalStringify(target.payload));
    assert.equal(actual, target.payload_sha256, target.id);
  }
});

test("rigid: browser renderer contains no dynamic HTML execution sinks", async () => {
  const source = await readFile(path.join(here, "app.js"), "utf8");
  for (const forbidden of [".innerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"]) {
    assert.equal(source.includes(forbidden), false, forbidden);
  }
  assert.equal(source.includes("textContent"), true);
});

function semanticMutations() {
  return [
    ["missing target", value => { value.fixture.targets = value.fixture.targets.filter(record => record.id !== "target:B0"); }],
    ["wrong target family", value => { value.fixture.occurrences[0].target_ref = "metadata:M1"; }],
    ["malformed identifier", value => { value.fixture.occurrences[0].id = "occurrence:bad/id"; }],
    ["duplicate identifier", value => { value.fixture.occurrences[1].id = "occurrence:O0"; }],
    ["unknown root field", value => { value.fixture.surprise = "not contracted"; }],
    ["unknown occurrence field", value => { value.fixture.occurrences[0].embedded = "not allowed"; }],
    ["missing relationship reference", value => { delete value.fixture.occurrences[0].relationship_ref; }],
    ["missing metadata reference", value => { delete value.fixture.occurrences[0].metadata_ref; }],
    ["embedded target body", value => { value.fixture.occurrences[0].target_ref = { id: "target:B0" }; }],
    ["altered chronological order", value => { value.fixture.views[0].occurrence_refs.reverse(); }],
    ["inconsistent view set", value => { value.fixture.views[1].occurrence_refs.pop(); }],
    ["digest tamper", value => { value.fixture.targets[0].payload_sha256 = "0".repeat(64); }],
    ["native null", value => { value.fixture.metadata[0].provenance = null; }],
    ["oversized string", value => { value.fixture.metadata[0].provenance = "x".repeat(8193); }],
    ["transformation input mismatch", async value => {
      const transform = find(value.fixture.targets, "target:T1");
      transform.payload.input_ref = "target:B1";
      await rehash(transform);
    }],
    ["relationship result mismatch", value => { value.fixture.relationships[0].result_ref = "target:B0"; }],
    ["embedded reference array", value => { value.fixture.occurrences[1].metadata_ref = ["metadata:M1"]; }],
    ["wrong kind", value => { value.fixture.metadata[0].kind = "relationship"; }],
    ["duplicate occurrence in view", value => { value.fixture.views[0].occurrence_refs[2] = "occurrence:O1"; }],
    ["malformed digest", value => { value.fixture.targets[2].payload_sha256 = "ABC"; }]
  ];
}

test("fuzzy: twenty semantic mutations are rejected deterministically", async t => {
  const mutations = semanticMutations();
  assert.equal(mutations.length, 20);
  for (const [name, mutate] of mutations) {
    await t.test(name, async () => {
      const candidate = clone(packet);
      await mutate(candidate);
      const first = await core.analyzePacket(candidate);
      const second = await core.analyzePacket(candidate);
      assert.ok(first.findings.length > 0, name);
      assert.deepEqual(first.findings, second.findings, name);
    });
  }
});

test("fuzzy: hostile markup remains inert record text", async () => {
  const candidate = clone(packet);
  const hostile = '<img src=x onerror="globalThis.compromised=true"><script>bad()</script>';
  candidate.fixture.metadata[0].provenance = hostile;
  const analysis = await core.analyzePacket(candidate, { enforceProfile: false });
  assert.equal(analysis.status, "valid");
  assert.equal(core.recordSummary(candidate.fixture.metadata[0]).includes(hostile), true);
  const appSource = await readFile(path.join(here, "app.js"), "utf8");
  assert.equal(appSource.includes("textContent"), true);
  assert.equal(appSource.includes(".innerHTML"), false);
});

function largeOccurrencePacket(count, viewCount = 2) {
  const candidate = clone(packet);
  candidate.fixture.pilot_id = `pilot:inspector-torture:occurrences:${count}:views:${viewCount}`;
  candidate.fixture.occurrences = Array.from({ length: count }, (_, index) => ({
    id: `occurrence:L${String(index).padStart(4, "0")}`,
    kind: "occurrence",
    target_ref: "target:B0",
    relationship_ref: "relationship:R1",
    metadata_ref: "metadata:M1"
  }));
  const ids = candidate.fixture.occurrences.map(record => record.id);
  let seed = 20261101;
  const random = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  candidate.fixture.views = Array.from({ length: viewCount }, (_, index) => {
    const order = [...ids];
    if (index === 1) order.reverse();
    else if (index > 1) {
      for (let cursor = order.length - 1; cursor > 0; cursor -= 1) {
        const swap = Math.floor(random() * (cursor + 1));
        [order[cursor], order[swap]] = [order[swap], order[cursor]];
      }
    }
    return {
      id: `view:L${String(index).padStart(3, "0")}`,
      kind: "view",
      purpose: `bounded_torture_view_${index}`,
      order_semantics: "inspection_permutation_only",
      occurrence_refs: order
    };
  });
  return candidate;
}

async function chainPacket(length) {
  const candidate = clone(packet);
  candidate.fixture.pilot_id = `pilot:inspector-torture:chain:${length}`;
  candidate.fixture.targets = [];
  candidate.fixture.relationships = [];
  candidate.fixture.metadata = [{
    id: "metadata:Chain",
    kind: "metadata",
    scope: "whole_block",
    provenance: `deterministic bounded chain of ${length} append operations`
  }];
  candidate.fixture.occurrences = [];
  const source = {
    id: "target:B0000",
    kind: "target",
    role: "immutable_text_block",
    payload: { encoding: "utf-8", text: "" },
    payload_sha256: ""
  };
  await rehash(source);
  candidate.fixture.targets.push(source);
  for (let index = 1; index <= length; index += 1) {
    const inputRef = `target:B${String(index - 1).padStart(4, "0")}`;
    const resultRef = `target:B${String(index).padStart(4, "0")}`;
    const operationRef = `target:T${String(index).padStart(4, "0")}`;
    const relationshipRef = `relationship:R${String(index).padStart(4, "0")}`;
    const operation = {
      id: operationRef,
      kind: "target",
      role: "transformation",
      payload: { operation: "append_text", argument: "x", input_ref: inputRef, result_ref: resultRef, scope_ref: "metadata:Chain" },
      payload_sha256: ""
    };
    const result = {
      id: resultRef,
      kind: "target",
      role: "immutable_text_block",
      payload: { encoding: "utf-8", text: "x".repeat(index) },
      payload_sha256: ""
    };
    await rehash(operation);
    await rehash(result);
    candidate.fixture.targets.push(operation, result);
    candidate.fixture.relationships.push({
      id: relationshipRef,
      kind: "relationship",
      meaning: "transforms_input_to_result",
      operation_ref: operationRef,
      input_ref: inputRef,
      result_ref: resultRef
    });
    for (const [suffix, targetRef] of [["I", inputRef], ["T", operationRef], ["R", resultRef]]) {
      candidate.fixture.occurrences.push({
        id: `occurrence:C${String(index).padStart(4, "0")}${suffix}`,
        kind: "occurrence",
        target_ref: targetRef,
        relationship_ref: relationshipRef,
        metadata_ref: "metadata:Chain"
      });
    }
  }
  const ids = candidate.fixture.occurrences.map(record => record.id);
  candidate.fixture.views = [
    { id: "view:ChainForward", kind: "view", purpose: "chain_forward_inspection", order_semantics: "input_transformation_result_per_step", occurrence_refs: ids },
    { id: "view:ChainReverse", kind: "view", purpose: "chain_reverse_inspection", order_semantics: "reverse_inspection_without_mutation", occurrence_refs: [...ids].reverse() }
  ];
  return candidate;
}

test("torture: accepted snapshot analyzes one thousand times", async () => {
  for (let index = 0; index < 1000; index += 1) {
    const analysis = await core.analyzePacket(packet);
    assert.equal(analysis.status, "valid", `iteration ${index}`);
  }
});

test("torture: 2,048-occurrence forward and reverse views resolve", async () => {
  const candidate = largeOccurrencePacket(2048, 2);
  const analysis = await core.analyzePacket(candidate, { enforceProfile: false });
  assert.equal(analysis.status, "valid");
  const comparison = core.compareViews(candidate.fixture, "view:L000", "view:L001");
  assert.equal(comparison.sameOccurrenceSet, true);
  assert.equal(comparison.sameOrder, false);
});

test("torture: sixty-four deterministic view permutations are stable", async () => {
  const candidate = largeOccurrencePacket(128, 64);
  const first = await core.analyzePacket(candidate, { enforceProfile: false });
  const second = await core.analyzePacket(candidate, { enforceProfile: false });
  assert.equal(first.status, "valid");
  assert.deepEqual(first.findings, second.findings);
});

test("torture: 128-step transformation chain resolves forward and backward", async () => {
  const candidate = await chainPacket(128);
  const analysis = await core.analyzePacket(candidate, { enforceProfile: false });
  assert.equal(analysis.status, "valid");
  assert.equal(candidate.fixture.targets.length, 257);
  assert.equal(candidate.fixture.relationships.length, 128);
  assert.equal(candidate.fixture.occurrences.length, 384);
});

test("torture: unresolved-reference storm is capped at 128 findings", async () => {
  const candidate = largeOccurrencePacket(512, 2);
  candidate.fixture.occurrences.forEach((record, index) => { record.target_ref = `target:Missing${String(index).padStart(4, "0")}`; });
  const analysis = await core.analyzePacket(candidate, { enforceProfile: false });
  assert.equal(analysis.findings.length, 128);
  assert.equal(analysis.findings.every(finding => finding.code === "unresolved_target"), true);
});

test("torture: deeply nested embedded reference rejects without recursion failure", async () => {
  const candidate = clone(packet);
  let nested = { leaf: "target:B0" };
  for (let index = 0; index < 1000; index += 1) nested = { nested };
  candidate.fixture.occurrences[0].target_ref = nested;
  const analysis = await core.analyzePacket(candidate);
  assert.equal(analysis.status, "invalid");
  assert.equal(analysis.findings.some(finding => finding.path.endsWith("target_ref") && finding.code === "wrong_type"), true);
});

test("torture: five hundred rejected candidates do not contaminate accepted snapshot", async () => {
  const before = core.canonicalStringify(packet);
  for (let index = 0; index < 500; index += 1) {
    const candidate = clone(packet);
    candidate.fixture.occurrences[index % 3].target_ref = `target:Missing${String(index).padStart(4, "0")}`;
    const analysis = await core.analyzePacket(candidate);
    assert.equal(analysis.status, "invalid");
  }
  assert.equal(core.canonicalStringify(packet), before);
  assert.equal((await core.analyzePacket(packet)).status, "valid");
});
