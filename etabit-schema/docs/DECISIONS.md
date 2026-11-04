# Etabit Schema — Decisions, evidence, and open contracts

**Record:** 2026-11-04, draft research transcription. No runtime authority, machine code, on-media format, or deployment implied.

## User-established architectural decisions

| Topic | Current position | Source classification |
| --- | --- | --- |
| System name | `ae-cryptography` = **Amorphous Experience Cryptography** | Direct user correction |
| External memory | `ae-external-memory` = **Amorphous Experience External Memory** | Direct user correction |
| Output | Etabit creates `eo-drive` = **Experience Orchestration Drive** | Direct user correction |
| Topology | Multiple source drives and referential/bitmap drives; arbitrary objects | Direct user correction |
| A/B/C lineage | Historic value / location / assembly three-drive example, not a fixed deployment | Historical concept + later user correction |
| Four-object example | `1`, `0`, `Error`, `Unknown` | Direct user proposal |
| OOB metadata | Each Etabit drive may have a meta disk; constructor may have scoped access; reader has none | Direct user correction |
| Cypher Disk | Internally distributed authority; decides metadata format, drive association, constructor protocol, disclosure, writes | Direct user corrections |
| Physical mechanism | Ceramic/mechanical Cypher implementation possible; mechanism not defined | Direct user possibility |
| Holonic behavior | Constituents can refuse cooperation; interlocks do not compel participation | Direct user correction |
| Process languages | Noncolliding typed namespaces; disabled codepage as nonexecuting text; language transfer gated | Direct user intent, detailed mechanism open |
| Renamed term | `UNSF` current, `USF` historical | Direct user correction |

## Derived safety distinctions (candidate, not ratified wire types)

- The stored `Error` symbol is distinct from a device read error. The stored `Unknown` symbol is distinct from an unresolved reference. Their 4-symbol algebra is **not defined**.
- Successful parsing or codepage translation never grants execution authority.
- The reader-to-out-of-band-meta path is disallowed. Constructor access is scoped and does not authorize automatic metadata disclosure through its outputs.
- Cypher decision-making requires independently enforceable boundaries; a description of authority is not a mechanism implementing authority.
- A reader may be allowed to return an admitted composed representation without knowing constructor-only semantic metadata.

## Open contracts

1. Durable on-media data/bitmap encoding, physical storage arrangement and cross-drive identities.
2. Referential grammar: order, multiplicity, recursion, bounds, conflicts and malformed references.
3. Source symbol encoding and semantics, alongside separately typed I/O/result/authority status.
4. Cypher constituent topology, refusal and collective decision mechanism (no invented quorum or veto).
5. Meta-disk format and association, constructor procedure, indirect disclosure control and write mediation.
6. Versioned codepage identities and independently admitted transformations.
7. `eo-drive` interface, persistent representation, recovery and independent attestation.
8. Complete historical provenance from original conversation/export and exact integration with the related document transformer.

## Source boundary

This draft is grounded in the Decomposition handoff dated 2026-10-31 and prior user-supplied design corrections. The handoff contains recovered historical summaries; it is not an authenticated full platform transcript. The related [textual transformer](../../syn-etabit-transformer-textual/README.md) reports a bounded CPU construction model; that does **not** establish a generalized Etabit drive or Cypher enforcement.

**Validation boundary:** JSON Schema validation checks only the declared document shape and fixed constraints. Executable isolation, physical reader/meta separation, encryption strength, recoverability and consensus remain **unimplemented/unverified in this project**.

## Next qualification

First define the smallest CPU-only typed-source and typed-reference resolution model, then independent negative/property tests covering unknown objects, failed reads, refusal, and indirect metadata disclosure. Do not reclassify a passing structural check as secure hardware authority.

## November 4 recursive-audit schema update: v0.2 draft

The [recursive-audit reconciliation](V0_2_AUDIT_RECONCILIATION.md) has now been committed alongside `etabit-project.v0.2.schema.json`, its example, and candidate negative tests. **v0.1 remains unchanged**; v0.2 is **DRAFT_NOT_ADMITTED**.

The new descriptive fields address identified gaps in typed *declarations* for arbitrary source objects, codepage-to-referential-drive association, explicit reference endpoints, separate four-symbol/operation-result boundaries, and possible Cypher constituent descriptions. The five Cypher responsibilities are now represented as an order-insensitive five-member set rather than a fixed-priority sequence.

These are draft field designs, not accepted wire types, parser APIs, storage formats, authorization protocols, or a guarantee that an authority boundary is enforced. Numeric IDs, physical layout, semantic calculus, collective voting, refusal mechanics, and an `eo-drive` reader/recovery protocol remain unresolved. Any validation is constrained to declared shapes and candidate local graph relationships.
