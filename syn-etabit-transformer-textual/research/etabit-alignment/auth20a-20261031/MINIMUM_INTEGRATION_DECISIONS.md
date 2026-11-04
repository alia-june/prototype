# Minimum decisions before Strmdocx ↔ sf-Etabit integration

Date: 2026-10-31 (America/New_York)  
Status: decision queue; no item is adopted by this report

The integration should not begin by absorbing WordNet or writing an adapter. It should begin by deciding what each record is, which authority owns it, where it may live, and how it is addressed. The following decisions are the minimum coherent set.

## Decision sequence

### MID-01 — Qualified namespace dictionary

Choose canonical, fully qualified names for:

- `sf-etabit.storage/D0`, `/D1`, `/D2`;
- `sf-registry.preservation/D0` through `/D5`;
- Strmdocx native layers;
- Strmdocx relative-map kinds;
- attestation and future overlay layers.

**Recommended default:** prohibit bare serialized `D0`, `D1`, or `D2`; aliases may exist only in a schema-qualified human view.

### MID-02 — Record-placement matrix

Place each Strmdocx record type in exactly one primary role, with explicit references to other roles:

- raw substrate reference;
- codepage, symbol and datatype;
- glyph, component, root and word definition;
- phrase, sentence, paragraph and document composition;
- source occurrence and locator;
- relation and theory projection;
- context and replacement ledger;
- provenance, derivation and attestation.

**Recommended default:** D0 stores none of these records. They reference D0 from D1/D2 or remain in an explicitly named overlay.

### MID-03 — D1/D2 construction boundary

Decide whether words are D1 molecules, D2 compositions, or have separate identities in both layers. Resolve every native layer consistently.

**Recommended default:** D1 owns codepage-symbol interpretation and reusable typed atoms/molecules; D2 owns occurrence-bearing ordered linguistic/document composition. If a word appears in both, use two qualified identities linked by an explicit reconstruction relation.

### MID-04 — Ordered occurrence grammar

Define:

- position and index base;
- repeated references;
- empty sequences;
- insertion/removal/replacement identity;
- nesting and recursion bounds;
- cycle policy;
- missing/unresolved references;
- deterministic reconstruction;
- x/y width units and overflow.

**Recommended default:** use an explicit finite ordered occurrence list in the first CPU model. Do not claim a membership bitmap alone is sufficient.

### MID-05 — Identity-role matrix

Separate:

- sf-UUID member identity;
- content/recipe digest;
- stream occurrence identity;
- source occurrence identity;
- map name/version/context identity;
- batch and operation identity;
- physical substrate/generation identity;
- attestation identity.

**Recommended default:** preserve existing SHA-256 recipe IDs as content identifiers only. Do not rename them sf-UUID. Keep the sf-UUID format open until AmorphousDrive resolves it.

### MID-06 — Change, replacement and lock semantics

Define which records are immutable, which may have successors, how a context selects a version, and what requires a new locked baseline.

**Recommended default:** replacement creates a new identity/context and preserves prior versions. A locked storage invariant is not contextually rewritten; deviations require explicit revision authority and a new lock.

### MID-07 — WordNet source representation

Define how archive bytes, tar member bytes, source records, source offsets and selected tokens are reconstructed and referenced without calling the archive a D0 object.

**Recommended default:** retain the original archive hash and member/offset/line hashes as external provenance; represent reconstructed source bytes above D0; preserve source occurrences separately from native definitions.

### MID-08 — Provenance, derivation and attestation placement

Define separate schemas for:

- provenance locator;
- construction recipe;
- derivation edge;
- source witness;
- validation result;
- attestation profile and disagreement.

**Recommended default:** none belongs on D0. Do not call a replay manifest an sf-Etabit attestation unless it satisfies an explicitly approved attestation profile.

### MID-09 — Source/decode/construction/enrichment map family

Specify the minimum independently versioned maps for WordNet transmigration:

1. source-faithful record map;
2. decoded WordNet-format map;
3. native spelling-construction map;
4. source relation map;
5. grammar/syntax/theory projection map;
6. inferred map;
7. synthesized/enriched map;
8. derivation and replacement ledgers.

**Recommended default:** source, decoded and constructed maps may proceed before inference only after persistence is decided. Inferred and synthesized maps must never overwrite source-derived identities.

### MID-10 — Storage and transaction contract

Define:

- reference-model locator;
- atomic publication unit;
- idempotency and duplicate behavior;
- lock/single-writer assumptions;
- crash/restart recovery;
- read-after-write and reload guarantees;
- corruption detection;
- capacity ceilings;
- migration/version handling;
- exact failure codes.

**Recommended default:** first implement a CPU-only local reference substrate with a declared noncanonical backend and strict atomic batches. Do not call it physical sf-Etabit or Cypher-controlled storage.

### MID-11 — Constructor and reader capabilities

Decide whether Decomposition's constructor-only metadata rule applies to the first reference model. If so, define two capability surfaces and test that the reader cannot access metadata directly or indirectly.

**Recommended default:** model the separation in the reference API if Etabit naming is used. Otherwise call the result a Strmdocx storage experiment, not an Etabit-conformant adapter.

### MID-12 — Authority and Cypher boundary

Decide whether Cypher authority is excluded, simulated as an inert external decision receipt, or fully specified later.

**Recommended default:** exclude collective Cypher governance from the first model. Accept only an external, non-self-authorizing decision record; do not invent quorum, veto or trust rules.

### MID-13 — Result and refusal typing

Separate:

- successful stored value;
- transport/read failure;
- unresolved reference;
- validation rejection;
- missing authority;
- constituent refusal/revocation;
- disagreement between witnesses.

**Recommended default:** never encode these as an overloaded `Error` or `Unknown` value.

### MID-14 — Validation and acceptance profile

Define what the first model must prove and what it cannot prove.

**Recommended minimum tests:**

- rigid: exact reconstruction, identity, ordering, duplicate occurrences, atomic rejection and reload;
- fuzzy-error: malformed references, missing targets, wrong namespaces, cross-generation IDs, unknown fields, limit violations and status/value confusion;
- torture: bounded concurrent readers, interrupted publication, restart/reload, corruption detection, resource ceilings and complete retained inputs;
- preservation: exact source hashes and no mutation outside the approved output root;
- proof language: local reference-model evidence only, not hardware, cryptographic, security or independent attestation.

## Dependencies

```text
MID-01 namespace
   ├─> MID-02 placement ─> MID-03 D1/D2 boundary
   ├─> MID-05 identity ───> MID-06 change/locks
   └─> MID-13 results

MID-03 + MID-04 + MID-05
   └─> MID-09 map family

MID-07 + MID-08 + MID-09 + MID-10
   └─> bounded persistence implementation proposal

MID-11 + MID-12 + MID-13
   └─> any Etabit authority or capability claim

All decisions
   └─> MID-14 acceptance profile
```

## Recommended next production proposal

The next proposal should be a **paper-level CPU substrate and record-placement contract**, not an implementation. It should resolve MID-01 through MID-06 and present alternatives for MID-07 through MID-13. Its output should be a reviewed specification and decision ledger only. After explicit approval of those decisions, a separate scope can implement one empty-store/create/read/reload packet with no WordNet bulk data, no grammar decoder, no Cypher governance, no GPU work and no agentic integration.
