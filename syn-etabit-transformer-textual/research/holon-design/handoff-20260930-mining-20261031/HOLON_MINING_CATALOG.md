# Holon Mining Catalog

Date: 2026-10-31. This is the human-readable index to the 44 source-classified records in `holon_mining_catalog.json`. It mines the supplied artifacts; it does not canonize candidate code or complete the open design.

## Controlling determination

The newest direct decision is **“everything is by reference.”** The September 30 handoff adds two essential constraints: a holoquary remains a holon, and relationships/coordination are broader than the earlier relative-depth hierarchy. Therefore reference is the connection mechanism, while relationship meaning, ordering views, ownership, metadata, occurrence identity and storage remain separately decidable.

## Current decisions and requirements

| Record | Mined determination |
| --- | --- |
| REF-001 | Everything is by reference; do not copy full target objects into every assembly. |
| HOLON-001 | Holon is the general semantic unit. |
| HOLON-002 | Holoquary is a holon operating compositionally, not another object species. |
| HOLON-003 | The design is recursive and modular; application semantics remain modular. |
| HOLON-004 | Identity describes the whole, roles and possible ways of acting. |
| HOLON-005 | Names, IDs, aliases, lineage and variations are identifier descriptions, not the whole identity. |
| STRUCT-001 | The current absolute structure is Wrapper → Compartment → Self/Identifiers or Composition/Holoquary-Holon/Data. |
| STRUCT-002 | Self-only, composition-only and three distinct empty states must not be collapsed. |
| CAT-001 | The complete structure catalog is required externally and internally as a holon. |
| SENT-001 | The new general representation uses cataloged sentinel holons while preserving source-native states. |
| REL-001 | Membership, composition, coordination and other relationships are broader than depth. |
| STRUCT-003 | The retained large hierarchy is Originator → Emitter → Source → eight named components. |

## Historical and application-specific material

| Record | Treatment |
| --- | --- |
| HIST-001 | Four-field wrapper plus ordered identifier/depth occurrences is a preserved earlier model, superseded as the universal foundation. |
| APP-001 | Story blocks and block cyphers are application forms; block is not proven identical to holon. |
| HIST-002 | UPTI-SF is historical, inactive, not used and excluded; lessons may be mined without activation. |
| UPST-01 / PAY-001 | The v0.1 packet is a nonrecursive application boundary, not native universal storage. |

## Reference lessons

- REF-002 separates a reference from the meaning of its relationship.
- REF-003 separates possession of a reference from authority to resolve or act on it.
- PAY-004 demonstrates an inert artifact reference whose file is not materialized.
- OPEN-001 preserves the unresolved choice between direct target references and occurrence/relationship/metadata reference structures.
- APP-002 proposes—but does not adopt—a nested packet as a resolved view over reference-native storage.

## Candidate implementation lessons

| Record | Lesson |
| --- | --- |
| PAY-002 | A closed versioned boundary can reject unknown envelope fields without making the native model closed. |
| PAY-003 | Epistemic claim labels, hints, IDs and provenance do not grant authority. |
| PAY-006 | Numerical data, knowledge, execution and provenance should not be silently consumed as one lane. |
| BOUND-001 | `READY_FOR_UPTI_HANDOFF` is local preparation, not delivery. |
| BOUND-002 | Exact-byte preservation is measurable and distinct from semantic equivalence. |
| BOUND-003 | Process-local replay and caller-declared capabilities are not durable or authenticated. |
| PATTERN-001 | Preserve source, stage, verify, commit, receipt and release only with authority is a useful inactive-spec lesson. |

## Conflicts that remain visible

| Record | Conflict |
| --- | --- |
| CONFLICT-001 | Native JSON null in the v0.1 application boundary versus sentinel holons in the later general design. |
| CONFLICT-002 | Nested closed packet bodies versus recursive, extensible, reference-addressed native representation. |
| PAY-007 | Nonrecursive application boundary versus recursive Holon composition. |
| MISSING-001 | Holoquary v1.2 is named and hashed but absent, so inherited-baseline comparison is unavailable. |

## Open decisions

1. **OPEN-001:** reference-occurrence, relationship, metadata and coordination representation.
2. **OPEN-002:** identifier lifecycle, namespace, edit stability, revisions and variants.
3. **OPEN-003:** holon atomics and block/holon granularity.
4. **OPEN-004:** minimum and empty serialization, Self/Composition coexistence and catalog placement.
5. **OPEN-005:** internal/external catalog and two-codex correspondence.
6. **OPEN-006:** attestation, recovery and regeneration semantics.

## Validation evidence

- TEST-001 records the current observed 10/10 v0.1 and 34/34 v0.2 local test passes.
- TEST-002 retains the nested UPTI-SF fuzzy/torture/crash claims as historical claims because the historical runtime and full tests are absent.
- TEST-003 preserves the two assistant-originated errors rather than rewriting the development history.
- ANTI-001 prohibits laundering preparation, fallback, recovery, syntax validity, hashes or local receipts into external success.

## Use boundary

The catalog supports future design discussion and Strmdocx crosswalking. It does not decide the native reference record, implement a resolver, assign identity policy, activate UPTI, adopt an inactive transport, create sentinels, or change the Strmdocx service.
