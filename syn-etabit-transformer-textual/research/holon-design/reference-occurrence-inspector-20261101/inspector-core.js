(function attachReferenceInspectorCore(root, factory) {
  "use strict";
  const api = factory();
  root.ReferenceInspectorCore = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(globalThis, function createReferenceInspectorCore() {
  "use strict";

  const KINDS = ["target", "relationship", "metadata", "occurrence", "view"];
  const COLLECTION_BY_KIND = {
    target: "targets",
    relationship: "relationships",
    metadata: "metadata",
    occurrence: "occurrences",
    view: "views"
  };
  const ID_PATTERN = /^(target|relationship|metadata|occurrence|view):[A-Za-z][A-Za-z0-9._-]{0,63}$/;
  const SHA256_PATTERN = /^[0-9a-f]{64}$/;

  function isPlainObject(value) {
    if (value === null || typeof value !== "object") return false;
    const prototype = Object.getPrototypeOf(value);
    return prototype === Object.prototype || prototype === null;
  }

  function canonicalStringify(value) {
    const active = new Set();
    function encode(current) {
      if (current === null) return "null";
      if (typeof current === "string") return JSON.stringify(current);
      if (typeof current === "boolean") return current ? "true" : "false";
      if (typeof current === "number") {
        if (!Number.isFinite(current)) throw new TypeError("non-finite number is not standard JSON");
        return JSON.stringify(current);
      }
      if (typeof current !== "object") throw new TypeError(`unsupported JSON value type: ${typeof current}`);
      if (active.has(current)) throw new TypeError("cyclic value cannot be canonicalized");
      active.add(current);
      let encoded;
      if (Array.isArray(current)) {
        encoded = `[${current.map(item => encode(item)).join(",")}]`;
      } else if (isPlainObject(current)) {
        const keys = Object.keys(current).sort();
        encoded = `{${keys.map(key => `${JSON.stringify(key)}:${encode(current[key])}`).join(",")}}`;
      } else {
        active.delete(current);
        throw new TypeError("non-plain object is not standard JSON data");
      }
      active.delete(current);
      return encoded;
    }
    return encode(value);
  }

  async function sha256Hex(text) {
    const subtle = globalThis.crypto && globalThis.crypto.subtle;
    if (!subtle || typeof TextEncoder === "undefined") return null;
    const bytes = new TextEncoder().encode(text);
    const digest = await subtle.digest("SHA-256", bytes);
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  }

  function deepClone(value) {
    if (typeof structuredClone === "function") return structuredClone(value);
    return JSON.parse(JSON.stringify(value));
  }

  function createFindingCollector(limit) {
    const findings = [];
    return {
      add(code, path, message) {
        if (findings.length < limit) findings.push({ code, path, message });
      },
      findings
    };
  }

  function scanJSONShape(rootValue, maxStringCharacters, add) {
    const stack = [{ path: "$", value: rootValue }];
    const seen = new WeakSet();
    while (stack.length) {
      const { path, value } = stack.pop();
      if (value === null) {
        add("native_null", path, "native JSON null is forbidden by the pilot contract");
        continue;
      }
      if (typeof value === "string") {
        if (value.length > maxStringCharacters) add("string_limit", path, `string exceeds ${maxStringCharacters} characters`);
        continue;
      }
      if (["number", "boolean"].includes(typeof value)) {
        if (typeof value === "number" && !Number.isFinite(value)) add("nonstandard_number", path, "number must be finite standard JSON");
        continue;
      }
      if (typeof value !== "object") {
        add("non_json_value", path, `unsupported value type: ${typeof value}`);
        continue;
      }
      if (seen.has(value)) {
        add("repeated_object", path, "repeated or cyclic object identity is not accepted");
        continue;
      }
      seen.add(value);
      if (Array.isArray(value)) {
        for (let index = value.length - 1; index >= 0; index -= 1) stack.push({ path: `${path}[${index}]`, value: value[index] });
      } else if (isPlainObject(value)) {
        const entries = Object.entries(value);
        for (let index = entries.length - 1; index >= 0; index -= 1) {
          const [key, child] = entries[index];
          stack.push({ path: `${path}.${key}`, value: child });
        }
      } else {
        add("non_plain_object", path, "only arrays and plain objects are accepted");
      }
    }
  }

  function exactFields(record, required, allowed, path, add) {
    const actual = new Set(Object.keys(record));
    for (const field of required) if (!actual.has(field)) add("missing_field", path, `missing required field ${field}`);
    for (const field of actual) if (!allowed.has(field)) add("unknown_field", path, `unknown field ${field}`);
  }

  function requireString(value, path, add) {
    if (typeof value !== "string") {
      add("wrong_type", path, "must be a scalar string");
      return false;
    }
    return true;
  }

  function orderedRecords(fixture) {
    const records = [];
    for (const kind of KINDS) {
      const collection = fixture && fixture[COLLECTION_BY_KIND[kind]];
      if (Array.isArray(collection)) records.push(...collection);
    }
    return records;
  }

  function buildIndex(fixture) {
    const byId = new Map();
    const byKind = Object.fromEntries(KINDS.map(kind => [kind, new Map()]));
    for (const record of orderedRecords(fixture)) {
      if (!isPlainObject(record) || typeof record.id !== "string" || !KINDS.includes(record.kind)) continue;
      if (!byId.has(record.id)) byId.set(record.id, record);
      if (!byKind[record.kind].has(record.id)) byKind[record.kind].set(record.id, record);
    }
    return { byId, byKind };
  }

  async function analyzePacket(packet, options = {}) {
    const contract = packet && packet.contract;
    const fixture = packet && packet.fixture;
    const limits = isPlainObject(contract && contract.limits) ? contract.limits : {};
    const maxErrors = Number.isInteger(options.maxErrors) ? options.maxErrors : Number.isInteger(limits.max_errors) ? limits.max_errors : 128;
    const maxStringCharacters = Number.isInteger(limits.max_string_characters) ? limits.max_string_characters : 8192;
    const collector = createFindingCollector(maxErrors);
    const add = collector.add;
    const enforceProfile = options.enforceProfile !== false;
    const digestResults = new Map();

    scanJSONShape(packet, maxStringCharacters, add);
    if (!isPlainObject(packet)) {
      add("root_type", "$", "display packet must be an object");
      return { status: "invalid", findings: collector.findings, digestResults, ...buildIndex({}) };
    }
    if (packet.schema !== "strmdocx-reference-occurrence-inspector-data/1") add("packet_schema", "$.schema", "unsupported display-packet schema");
    if (packet.role !== "read_only_resolved_display_packet") add("packet_role", "$.role", "display packet must declare its read-only resolved role");
    if (!Array.isArray(packet.source_files) || packet.source_files.length !== 2) add("source_files", "$.source_files", "exactly two source-file identities are required");

    if (!isPlainObject(contract)) add("contract_type", "$.contract", "contract must be an object");
    if (!isPlainObject(fixture)) {
      add("fixture_type", "$.fixture", "fixture must be an object");
      return { status: "invalid", findings: collector.findings, digestResults, ...buildIndex({}) };
    }

    const rootRequired = new Set(contract?.root_schema?.required_fields || []);
    const rootAllowed = new Set(contract?.root_schema?.allowed_fields || []);
    exactFields(fixture, rootRequired, rootAllowed, "$.fixture", add);
    if (fixture.format !== contract?.fixture_format) add("fixture_format", "$.fixture.format", "does not match contract fixture_format");
    requireString(fixture.pilot_id, "$.fixture.pilot_id", add);

    const byId = new Map();
    const byKind = Object.fromEntries(KINDS.map(kind => [kind, new Map()]));
    const recordPaths = new Map();

    for (const kind of KINDS) {
      const schema = contract?.record_schemas?.[kind];
      const collectionName = schema?.collection || COLLECTION_BY_KIND[kind];
      const collection = fixture[collectionName];
      const collectionPath = `$.fixture.${collectionName}`;
      if (!Array.isArray(collection)) {
        add("collection_type", collectionPath, "must be an array");
        continue;
      }
      const collectionLimit = kind === "view" ? limits.max_views : limits.max_collection_records;
      if (Number.isInteger(collectionLimit) && collection.length > collectionLimit) add("collection_limit", collectionPath, `contains ${collection.length} records; limit is ${collectionLimit}`);
      const inspectCount = Number.isInteger(collectionLimit) ? Math.min(collection.length, collectionLimit + 1) : collection.length;
      for (let index = 0; index < inspectCount; index += 1) {
        const record = collection[index];
        const path = `${collectionPath}[${index}]`;
        if (!isPlainObject(record)) {
          add("record_type", path, "record must be an object");
          continue;
        }
        exactFields(record, new Set(schema?.required_fields || []), new Set(schema?.allowed_fields || []), path, add);
        if (record.kind !== kind) add("record_kind", `${path}.kind`, `must be exactly ${kind}`);
        if (requireString(record.id, `${path}.id`, add)) {
          if (!ID_PATTERN.test(record.id)) add("malformed_id", `${path}.id`, "malformed pilot identifier");
          if (!record.id.startsWith(schema?.id_prefix || `${kind}:`)) add("wrong_id_prefix", `${path}.id`, `must start with ${schema?.id_prefix || `${kind}:`}`);
          if (byId.has(record.id)) add("duplicate_id", `${path}.id`, `duplicate identifier first used at ${recordPaths.get(record.id)}`);
          else {
            byId.set(record.id, record);
            recordPaths.set(record.id, path);
          }
          if (!byKind[kind].has(record.id)) byKind[kind].set(record.id, record);
        }
      }
    }

    for (const [id, target] of byKind.target) {
      const path = recordPaths.get(id) || "$.fixture.targets";
      if (!requireString(target.role, `${path}.role`, add)) continue;
      if (!isPlainObject(target.payload)) add("payload_type", `${path}.payload`, "payload must be an object");
      else if (target.role === "immutable_text_block") {
        const keys = Object.keys(target.payload).sort().join(",");
        if (keys !== "encoding,text") add("text_payload_shape", `${path}.payload`, "immutable text payload must contain exactly encoding and text");
        if (target.payload.encoding !== "utf-8") add("text_encoding", `${path}.payload.encoding`, "must be exactly utf-8");
        requireString(target.payload.text, `${path}.payload.text`, add);
      } else if (target.role === "transformation") {
        const expected = ["argument", "input_ref", "operation", "result_ref", "scope_ref"].join(",");
        if (Object.keys(target.payload).sort().join(",") !== expected) add("transform_payload_shape", `${path}.payload`, "transformation payload fields are not exact");
        for (const field of ["argument", "input_ref", "operation", "result_ref", "scope_ref"]) requireString(target.payload[field], `${path}.payload.${field}`, add);
        if (target.payload.operation !== "append_text") add("unsupported_operation", `${path}.payload.operation`, "unsupported pilot transformation");
      } else add("unsupported_role", `${path}.role`, "unsupported target role");

      const expectedDigest = target.payload_sha256;
      if (!requireString(expectedDigest, `${path}.payload_sha256`, add) || !SHA256_PATTERN.test(expectedDigest || "")) {
        add("digest_format", `${path}.payload_sha256`, "must be 64 lowercase hexadecimal characters");
        digestResults.set(id, { status: "mismatch", expected: expectedDigest || "", actual: null });
      } else if (isPlainObject(target.payload)) {
        try {
          const canonical = canonicalStringify(target.payload);
          const actualDigest = await sha256Hex(canonical);
          if (actualDigest === null) digestResults.set(id, { status: "unavailable", expected: expectedDigest, actual: null });
          else if (actualDigest !== expectedDigest) {
            digestResults.set(id, { status: "mismatch", expected: expectedDigest, actual: actualDigest });
            add("digest_mismatch", `${path}.payload_sha256`, "does not match canonical payload digest");
          } else digestResults.set(id, { status: "verified", expected: expectedDigest, actual: actualDigest });
        } catch (error) {
          digestResults.set(id, { status: "mismatch", expected: expectedDigest, actual: null });
          add("canonicalization_failure", `${path}.payload`, `cannot be canonically serialized: ${error.name || "Error"}`);
        }
      }
    }

    for (const [id, relationship] of byKind.relationship) {
      const path = recordPaths.get(id) || "$.fixture.relationships";
      requireString(relationship.meaning, `${path}.meaning`, add);
      for (const field of ["operation_ref", "input_ref", "result_ref"]) {
        if (requireString(relationship[field], `${path}.${field}`, add) && !byKind.target.has(relationship[field])) add("unresolved_target", `${path}.${field}`, "unresolved target reference");
      }
    }

    for (const [id, metadata] of byKind.metadata) {
      const path = recordPaths.get(id) || "$.fixture.metadata";
      requireString(metadata.scope, `${path}.scope`, add);
      requireString(metadata.provenance, `${path}.provenance`, add);
    }

    for (const [id, occurrence] of byKind.occurrence) {
      const path = recordPaths.get(id) || "$.fixture.occurrences";
      const rules = [["target_ref", "target"], ["relationship_ref", "relationship"], ["metadata_ref", "metadata"]];
      for (const [field, expectedKind] of rules) {
        const reference = occurrence[field];
        if (requireString(reference, `${path}.${field}`, add) && !byKind[expectedKind].has(reference)) add(`unresolved_${expectedKind}`, `${path}.${field}`, `unresolved ${expectedKind} reference`);
      }
    }

    const viewSets = [];
    for (const [id, view] of byKind.view) {
      const path = recordPaths.get(id) || "$.fixture.views";
      requireString(view.purpose, `${path}.purpose`, add);
      requireString(view.order_semantics, `${path}.order_semantics`, add);
      if (!Array.isArray(view.occurrence_refs)) {
        add("view_refs_type", `${path}.occurrence_refs`, "must be an array of scalar references");
        continue;
      }
      if (Number.isInteger(limits.max_occurrence_refs_per_view) && view.occurrence_refs.length > limits.max_occurrence_refs_per_view) add("view_refs_limit", `${path}.occurrence_refs`, "exceeds occurrence-reference limit");
      const inspected = Number.isInteger(limits.max_occurrence_refs_per_view) ? view.occurrence_refs.slice(0, limits.max_occurrence_refs_per_view + 1) : view.occurrence_refs;
      const validRefs = [];
      inspected.forEach((reference, index) => {
        if (requireString(reference, `${path}.occurrence_refs[${index}]`, add)) {
          validRefs.push(reference);
          if (!byKind.occurrence.has(reference)) add("unresolved_occurrence", `${path}.occurrence_refs[${index}]`, "unresolved occurrence reference");
        }
      });
      if (new Set(validRefs).size !== validRefs.length) add("duplicate_view_occurrence", `${path}.occurrence_refs`, "duplicate occurrence reference within view");
      viewSets.push([id, new Set(validRefs)]);
    }
    if (viewSets.length) {
      const [baselineId, baseline] = viewSets[0];
      for (const [id, current] of viewSets.slice(1)) {
        const equal = current.size === baseline.size && [...current].every(item => baseline.has(item));
        if (!equal) add("view_set_mismatch", `view:${id}`, `occurrence set differs from ${baselineId}`);
      }
    }

    for (const [id, target] of byKind.target) {
      if (target.role !== "transformation" || !isPlainObject(target.payload)) continue;
      const path = recordPaths.get(id) || "$.fixture.targets";
      const { input_ref: inputRef, result_ref: resultRef, scope_ref: scopeRef } = target.payload;
      if (typeof inputRef === "string" && !byKind.target.has(inputRef)) add("unresolved_target", `${path}.payload.input_ref`, "unresolved target reference");
      if (typeof resultRef === "string" && !byKind.target.has(resultRef)) add("unresolved_target", `${path}.payload.result_ref`, "unresolved target reference");
      if (typeof scopeRef === "string" && !byKind.metadata.has(scopeRef)) add("unresolved_metadata", `${path}.payload.scope_ref`, "unresolved metadata reference");
      const relationships = [...byKind.relationship.values()].filter(record => record.operation_ref === id);
      if (!relationships.length) add("missing_transform_relationship", path, "transformation is not named by any relationship");
      for (const relationship of relationships) {
        if (relationship.input_ref !== inputRef || relationship.result_ref !== resultRef) add("relationship_disagreement", path, "transformation input/result references disagree with relationship");
      }
      const source = byKind.target.get(inputRef);
      const result = byKind.target.get(resultRef);
      if (target.payload.operation === "append_text" && source?.payload && result?.payload && typeof source.payload.text === "string" && typeof result.payload.text === "string" && typeof target.payload.argument === "string" && source.payload.text + target.payload.argument !== result.payload.text) add("transformation_result", path, "append_text result does not equal source text plus argument");
    }

    if (enforceProfile) validateExpectedProfile(fixture, contract, byKind, add);

    const findings = collector.findings;
    const digestUnavailable = [...digestResults.values()].some(result => result.status === "unavailable");
    const status = findings.length ? "invalid" : digestUnavailable ? "partial" : "valid";
    return { status, findings, digestResults, byId, byKind, recordPaths };
  }

  function validateExpectedProfile(fixture, contract, byKind, add) {
    const profile = contract?.expected_profile;
    if (!isPlainObject(profile)) {
      add("profile_missing", "$.contract.expected_profile", "expected profile must be an object");
      return;
    }
    if (fixture.pilot_id !== profile.pilot_id) add("profile_pilot_id", "$.fixture.pilot_id", "does not match expected pilot profile");
    for (const [profileKey, kind] of [["target_ids", "target"], ["relationship_ids", "relationship"], ["metadata_ids", "metadata"]]) {
      const expected = new Set(profile[profileKey] || []);
      const actual = new Set(byKind[kind].keys());
      if (expected.size !== actual.size || [...actual].some(id => !expected.has(id))) add("profile_ids", `$.fixture.${COLLECTION_BY_KIND[kind]}`, `IDs do not match expected ${profileKey}`);
    }
    const bindings = profile.occurrence_bindings || {};
    if (byKind.occurrence.size !== Object.keys(bindings).length || [...byKind.occurrence.keys()].some(id => !bindings[id])) add("profile_occurrences", "$.fixture.occurrences", "IDs do not match expected occurrence bindings");
    for (const [id, expected] of Object.entries(bindings)) {
      const actual = byKind.occurrence.get(id);
      if (!actual) continue;
      for (const [field, value] of Object.entries(expected)) if (actual[field] !== value) add("profile_binding", `occurrence:${id}.${field}`, "does not match expected binding");
    }
    const orders = profile.view_orders || {};
    if (byKind.view.size !== Object.keys(orders).length || [...byKind.view.keys()].some(id => !orders[id])) add("profile_views", "$.fixture.views", "IDs do not match expected inspection views");
    for (const [id, expected] of Object.entries(orders)) {
      const actual = byKind.view.get(id)?.occurrence_refs;
      if (!Array.isArray(actual) || actual.length !== expected.length || actual.some((value, index) => value !== expected[index])) add("profile_view_order", `view:${id}.occurrence_refs`, "does not match expected profile order");
    }
    const transformation = profile.transformation || {};
    const target = byKind.target.get(transformation.target_ref);
    const relationship = byKind.relationship.get(transformation.relationship_ref);
    const metadata = byKind.metadata.get(transformation.metadata_ref);
    const source = byKind.target.get(transformation.input_ref);
    const result = byKind.target.get(transformation.result_ref);
    if (target?.payload) {
      for (const field of ["input_ref", "result_ref", "operation", "argument"]) if (target.payload[field] !== transformation[field]) add("profile_transformation", `target:${transformation.target_ref}.payload.${field}`, "does not match expected transformation");
      if (target.payload.scope_ref !== transformation.metadata_ref) add("profile_scope", `target:${transformation.target_ref}.payload.scope_ref`, "does not match expected metadata reference");
    }
    if (relationship && relationship.meaning !== profile.relationship_meaning) add("profile_relationship", "relationship:meaning", "does not match expected profile");
    if (metadata && metadata.scope !== profile.metadata_scope) add("profile_metadata", "metadata:scope", "does not match expected profile");
    if (source?.payload?.text !== profile.source_text) add("profile_source", "source:text", "does not match expected profile");
    if (result?.payload?.text !== profile.result_text) add("profile_result", "result:text", "does not match expected profile");
  }

  function resolveView(fixture, viewId, index = buildIndex(fixture)) {
    const view = index.byKind.view.get(viewId);
    if (!view || !Array.isArray(view.occurrence_refs)) return null;
    return {
      view,
      entries: view.occurrence_refs.map((occurrenceId, position) => {
        const occurrence = index.byKind.occurrence.get(occurrenceId) || null;
        const target = occurrence ? index.byKind.target.get(occurrence.target_ref) || null : null;
        const relationship = occurrence ? index.byKind.relationship.get(occurrence.relationship_ref) || null : null;
        const metadata = occurrence ? index.byKind.metadata.get(occurrence.metadata_ref) || null : null;
        return { position, occurrenceId, occurrence, target, relationship, metadata };
      })
    };
  }

  function compareViews(fixture, leftId, rightId) {
    const index = buildIndex(fixture);
    const left = resolveView(fixture, leftId, index);
    const right = resolveView(fixture, rightId, index);
    if (!left || !right) return null;
    const leftIds = left.entries.map(entry => entry.occurrenceId);
    const rightIds = right.entries.map(entry => entry.occurrenceId);
    const leftSet = new Set(leftIds);
    const rightSet = new Set(rightIds);
    return {
      left,
      right,
      sameOccurrenceSet: leftSet.size === rightSet.size && [...leftSet].every(id => rightSet.has(id)),
      sameOrder: leftIds.length === rightIds.length && leftIds.every((id, indexValue) => id === rightIds[indexValue]),
      historyMutated: false,
      rollbackPerformed: false
    };
  }

  function referenceIds(record) {
    if (!isPlainObject(record)) return [];
    const references = [];
    for (const [key, value] of Object.entries(record)) {
      if (key.endsWith("_ref") && typeof value === "string") references.push(value);
      if (key === "occurrence_refs" && Array.isArray(value)) references.push(...value.filter(item => typeof item === "string"));
      if (key === "payload" && isPlainObject(value)) references.push(...referenceIds(value));
    }
    return [...new Set(references)];
  }

  function recordSummary(record) {
    if (!record) return "Unresolved record.";
    if (record.kind === "target" && record.role === "immutable_text_block") return `Immutable UTF-8 text block: ${JSON.stringify(record.payload?.text ?? "")}`;
    if (record.kind === "target" && record.role === "transformation") return `${record.payload?.operation || "Transformation"} ${JSON.stringify(record.payload?.argument ?? "")} from ${record.payload?.input_ref || "?"} to ${record.payload?.result_ref || "?"}.`;
    if (record.kind === "relationship") return `${record.meaning || "Relationship"}: ${record.operation_ref || "?"} maps ${record.input_ref || "?"} to ${record.result_ref || "?"}.`;
    if (record.kind === "metadata") return `${record.scope || "Unspecified"} scope. ${record.provenance || ""}`;
    if (record.kind === "occurrence") return `Participation of ${record.target_ref || "?"}, bound by relationship and metadata references.`;
    if (record.kind === "view") return `${record.purpose || "Inspection view"}; order is local to this view only.`;
    return "Record details.";
  }

  function targetPreview(target) {
    if (!target) return "Unresolved target";
    if (target.role === "immutable_text_block") return JSON.stringify(target.payload?.text ?? "");
    if (target.role === "transformation") return `${target.payload?.operation || "operation"} ${JSON.stringify(target.payload?.argument ?? "")}`;
    return target.id || "Target";
  }

  return Object.freeze({
    KINDS: Object.freeze([...KINDS]),
    COLLECTION_BY_KIND: Object.freeze({ ...COLLECTION_BY_KIND }),
    analyzePacket,
    buildIndex,
    canonicalStringify,
    compareViews,
    deepClone,
    isPlainObject,
    orderedRecords,
    recordSummary,
    referenceIds,
    resolveView,
    sha256Hex,
    targetPreview
  });
});
