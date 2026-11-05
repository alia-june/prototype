> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Offloading Heuristics

**Status:** `[GENERATED-PROPOSAL]` pending acceptance. These are deterministic workload-management rules, not measured guarantees about model memory.

## 1. Objective

Reduce active prompt burden while preserving mission, authority, provenance, material uncertainty, and recovery state. The system must never claim an exact context-occupancy percentage unless the runtime exposes one.

## 2. Observable pressure signals

Use observable task structure rather than invented token or memory metrics.

| Signal | Suggested response |
|---|---|
| More than 3 substantial artifacts | Create a source index and pointer ledger |
| More than 12 material claims | Externalize a claim ledger; keep only unresolved/high-impact claims resident |
| More than 5 tool actions | Create an action ledger and checkpoint before the next mutation |
| Two or more independent questions | Create bounded shards with separate terminal conditions |
| Repeated definitions or locks | Store once verbatim and reference by stable ID |
| Completed branch no longer affects active decisions | Archive a validated terminal packet |
| Compression or model/session transfer is imminent | Load the `handoff` profile and validate the receiver packet |
| Any consequential file mutation | Load `artifact_edit`; work from a verified copy |
| Any physical/boot/firmware/storage mutation | Load `bare_metal`; do not downgrade |
| Time-sensitive, quoted, niche, disputed, legal, medical, financial, or externally attributable claim | Load `research` and verify current primary sources |
| Mission, actor, authority, source, or target is unclear | Do not offload the ambiguity; halt the affected branch |

Thresholds are workload triggers, not scientific limits. A single high-consequence item can require the full profile even when all counts are below threshold.

## 3. Three-layer memory layout

### Layer A — resident kernel

Always active: mission capsule, exact user definitions, immutable locks, source order, generated-text marking, terminal condition, material unknowns, actor/authority state, and current version identity.

### Layer B — active working set

Only what is required for the current phase: relevant source excerpts, active claims, current transformation plan, immediate tool targets, and verification criteria.

### Layer C — external ledger

Stable artifacts containing source catalogues, complete claim/error/action/version ledgers, completed branches, rejected alternatives, full citations, detailed logs, and prior validated compressions.

Promotion from Layer C to B requires retrieval and verification. Compression from B to C must preserve provenance and uncertainty.

## 4. Offload decision procedure

```text
1. Does the item determine mission, authority, actor, scope, terminal state, or recovery?
   yes -> keep resident.
2. Is the item required for the current phase?
   yes -> keep in active working set.
3. Is it verified evidence or a completed validated branch?
   yes -> externalize with stable pointer and checksum/version when available.
4. Is it generated, disputed, unknown, or rejected?
   yes -> externalize only with its status intact; never compress into fact.
5. Would losing the item change a material decision?
   yes -> include it in the next compression/handoff packet.
6. Otherwise archive it and retain only the pointer.
```

## 5. Subtask splitting rules

A task may be split only when outputs can be independently validated and no shard must decide another shard's mission or authority. Good shard boundaries include source retrieval, citation verification, mechanical comparison, checksum generation, schema validation, and independent section drafting with a fixed outline.

Do not shard an unresolved definition, a canon decision, a promotion decision, a destructive authorization, a disputed factual conclusion, or the final mission-consistency check.

## 6. Deterministic tool preference

Prefer deterministic tools for counting, hashing, sorting, parsing, diffing, schema validation, link checking, and reproducible assembly. The LLM interprets results but does not invent tool output. A tool success code proves only that the process exited successfully; it does not prove semantic correctness or task completion.

## 7. Return gate

Every offloaded result returns with source pointers, limitations, generated status, and terminal state. The parent verifies it before use. A returning shard cannot:

- change the active mission;
- promote itself or another version;
- mark generated material as user-authored;
- erase conflicts or unknowns;
- issue new tool authority;
- declare whole-task completion.

## 8. Recovery from overload

When active state becomes unreliable:

1. Stop new generation.
2. Preserve the current Mission Capsule and working-copy/version identifiers.
3. Externalize verified ledgers.
4. Produce a validated compression.
5. Start a continuation using the handoff profile.
6. Have the receiver restate and verify the capsule before resuming.

## 9. When offloading cannot run

Do not treat unavailable offloading as permission to discard resident state or to fabricate a successful checkpoint.

1. Record the observed capability failure without inferring its cause.
2. Enter degraded continuity mode and freeze mission, scope, actor, authority, and terminal condition.
3. Cancel unopened branches.
4. Permit at most one reversible atomic step whose inputs and validation rule remain resident.
5. Prefer a verified new-child checkpoint when a safe write surface remains available.
6. Otherwise emit the degraded-continuation packet in the current response.
7. Block consequential mutation, compression, handoff, and claims of persistence until the missing capability is restored or the mission is explicitly contracted.
8. Stop when any material state required by the next step is no longer resident.

No-offload fallback preserves a bounded continuation surface. It does not replace unavailable memory, storage, retrieval, recovery, or independent verification.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
