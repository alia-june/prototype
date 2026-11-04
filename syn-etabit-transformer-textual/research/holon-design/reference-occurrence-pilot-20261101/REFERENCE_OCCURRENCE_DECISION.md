# Reference-Occurrence Pilot Decision

Date: 2026-11-01  
Status: approved bounded pilot; not general Holon canon and not Strmdocx runtime integration.

## Production clearance

The user approved the concrete occurrence/reference-holon pilot proposal with **“yes”** on 2026-11-01. The clearance covers only this directory, its tiny immutable-text fixture, its contract and explanatory documents, and its rigid, deterministic fuzzy, and bounded torture validation.

It does not authorize a transport, resolver service, database, native storage layer, GPU representation, WordNet ingestion, sentinel catalog, general transformation algebra, agentic control, or changes to the existing Strmdocx service.

## Governing basis

This pilot is derived from the following approved mining outputs in the sibling `handoff-20260930-mining-20261031` directory:

- `REFERENCE_MODEL.md` — “Everything is by reference,” separation of holon/reference/relationship, and the two candidate occurrence forms.
- `DECISIONS_CONFLICTS_AND_OPEN_QUESTIONS.md` — occurrence identity is the first implementation-affecting open decision.
- `PAYLOAD_AND_REFERENCE_BOUNDARY.md` — target, occurrence, relationship, metadata, transformation, and result references must remain distinguishable.
- `STRMDOCX_HOLON_CROSSWALK.md` — a small example with two immutable text blocks, one transformation, one result, relationship/metadata, and two inspection orders.
- `VALIDATION.md` — proof boundaries and source-package validation limits.

The user selected the occurrence/reference-holon branch by approving the proposal that contrasted it with direct target entries.

## Adopted only for this pilot

An ordered view references occurrence holons. Each occurrence holon then references:

1. one independently represented target holon;
2. one independently represented relationship holon; and
3. one independently represented metadata holon.

The fixture uses:

- `target:B0` — immutable UTF-8 text block containing `abc`;
- `target:T1` — independently identified append-text transformation;
- `target:B1` — immutable UTF-8 result block containing `abc!`;
- `relationship:R1` — explicit transformation relationship linking T1, B0, and B1 by reference;
- `metadata:M1` — whole-block scope and fixture provenance;
- `occurrence:O0`, `occurrence:O1`, and `occurrence:O2` — references to B0, T1, and B1 respectively;
- `view:V0` — chronological inspection order O0, O1, O2; and
- `view:V1` — reverse inspection order O2, O1, O0.

The reverse view changes traversal only. It does not rewrite, roll back, reverse, or replace history.

## Rules exercised

1. Every record has a unique pilot identifier.
2. Views contain occurrence references, not embedded occurrence or target bodies.
3. Occurrences contain exactly target, relationship, and metadata references in addition to their own identity and kind.
4. The same occurrence identifiers can participate in more than one view.
5. Array position supplies order only within that view.
6. Array order does not imply ownership, containment, authority, or lifetime.
7. Relationship meaning is explicit and cannot be inferred from adjacency.
8. Metadata is independently addressed rather than nested into the occurrence.
9. Source and result text blocks are immutable fixture records with deterministic payload digests.
10. Transformation identity is distinct from result identity.
11. Native JSON `null`, duplicate properties, nonstandard numeric constants, and unknown fields are rejected.
12. A rejected document cannot modify the accepted fixture held by the harness.

## Explicitly not decided

This pilot does not decide:

- a universal identifier format or namespace;
- whether every real occurrence must be a holon;
- the universal Holon wrapper serialization;
- ownership, deletion, lifetime, garbage collection, or revision policy;
- cycles, cycle semantics, or a general recursive traversal policy;
- whether arbitrary repeated occurrences are legal in every composition;
- a canonical ordering view for real documents;
- sentinel identities or native special-state encoding;
- physical block/storage layout;
- semantic equivalence, cancellation, commutation, or bypass of transformations;
- rendering fidelity for Markdown, HTML, Python, DOCX, or GPU forms;
- effect authority, transport, delivery, or independent attestation.

## Decision consequence

The pilot supplies evidence that occurrence-addressed inspection orders can reference the same immutable source, transformation, and result records without copying those records into each order. It is a testable design probe, not a declaration that the probe is the final native architecture.
