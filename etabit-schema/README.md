# Etabit Schema — research project

**Status:** DRAFT / NOT ADMITTED. This directory is a standalone schema research project for the **Etabit** multi-drive construction architecture. It is **not** a disk formatter, runtime interpreter, on-media specification, cryptographic proof, or execution authority.

## Scope and lineage

- **Amorphous Experience Cryptography** (`ae-cryptography`) includes the **Amorphous Experience External Memory** (`ae-external-memory`) direction.
- **Etabit** constructs an **Experience Orchestration Drive** (`eo-drive`).
- Historical `Etadisk` A/B/C (value, lookup, assembly) was an example; generalized Etabit can contain any number of heterogeneous source and referential/bitmap drives.
- Source drives can contain arbitrary objects. One illustrative source repertoire is `1`, `0`, `Error`, `Unknown`. A successfully read `Error` or `Unknown` *symbol* must remain distinguishable from a failed read or unresolved reference.
- Referencing may assemble particles, atoms, molecules and higher constructs as examples, **not** a mandatory hierarchy. Order, repetition, and exact bitmap grammar are unresolved.
- Each drive **may** have an out-of-band meta disk, accessible only to a suitably authorized constructor and **inaccessible to an Etabit reader**. Metadata is not automatically disclosed in reader-visible output.
- The **Cypher Disk is internally distributed authority**, deciding metadata format, physical associations, constructor protocol, disclosure controls, and write authority. No quorum, voting mechanism, key schedule, or physical mechanism is yet prescribed; ceramic/mechanical construction remains a possibility.
- Each holonic participant retains its right to refuse or revoke cooperation. A reference or interlock does not override refusal.
- Process-specific codepages and a disabled text-only codepage are distinct from execution permission. `UNSF` supersedes historical `USF`.

## Project layout

- [schema/etabit-project.schema.json](schema/etabit-project.schema.json) — **JSON Schema 2020-12** for a *research descriptor*, with explicit security and provenance constraints.
- [examples/four-symbol-source.json](examples/four-symbol-source.json) — illustrative descriptor using typed sentinel strings instead of JSON `null`.
- [docs/DECISIONS.md](docs/DECISIONS.md) — source-backed decisions, open contracts and implementation boundaries.

### Recursive-audit revision: v0.2 (additional noncanonical draft)

- [schema/etabit-project.v0.2.schema.json](schema/etabit-project.v0.2.schema.json) — versioned JSON Schema research descriptor with named object declarations, drive/object references, codepage-associated referential drive IDs, typed boundary declarations and internal Cypher constituent descriptions.
- [examples/four-symbol-source.v0.2.json](examples/four-symbol-source.v0.2.json) — independent v0.2 example; preserves `1`, `0`, `Error`, and `Unknown` as source objects and does not equate them to operational statuses.
- [docs/V0_2_AUDIT_RECONCILIATION.md](docs/V0_2_AUDIT_RECONCILIATION.md) — reconciliation against the November 4 recursive 20-item schema traceability audit; corrected the accidental fixed order of Cypher responsibilities.
- [tests/test_v0_2.py](tests/test_v0_2.py) — optional offline document-level JSON Schema and referential-integrity negative checks (`jsonschema` dependency). This validates declarations only, never hardware isolation, holonic consent or distributed authority.

The original v0.1 schema/example are **retained unchanged**, not silently promoted or replaced. v0.2 is also `DRAFT_NOT_ADMITTED`, with deliberately unresolved reference grammar, on-media storage, semantic payload typing, read-result transport, Cypher collective-decision protocol, and reader/constructor enforcement.

Run the optional test with `python -m pip install jsonschema` and `python etabit-schema/tests/test_v0_2.py`. Passing is not evidence of a deployed Etabit drive.

## How to use

Inspect the schema and example as **data**, not instructions. They describe the intended boundaries but do not enforce them. A JSON Schema validator can check a descriptor's declared shape and fixed values; it **cannot** certify disk access isolation, physical layout, Cypher collective decisions, safe execution, or cryptographic security.

No numeric codepage IDs, Etabit bitcodes, byte layouts, physical addressing, voting protocols or active authority are assigned here.

## Relation to Syn-Etabit Transformer — Textual

[Syn-Etabit Transformer — Textual](../syn-etabit-transformer-textual/README.md) already documents a reference-addressed document/map model and a bounded CPU implementation. This schema project is **separate** and describes the wider Etabit drive architecture. The related implementation is not evidence of a deployed general Etabit drive, an `eo-drive`, or a Cypher Disk.

## Relation to sf-AmorphDataDrive

[sf-AmorphDataDrive](../sf-amorph-data-drive/README.md) is a separate strict raw-substrate architecture and candidate Etabit source/substrate profile. The relationship is not admitted integration.

Etabit does not relax sf-AmorphDataDrive D0: identity, metadata, datatype, encoding, attestation, reconstruction, filesystem, partition, and composition remain outside raw D0. Arbitrary-object sources, out-of-band meta disks, generic IDs, and Cypher authority do not automatically map to D0, member sf-UUID, or the ID/data/metadata direction.

Integration requires a reviewed cross-map for identity, references, bitmap order and multiplicity, metadata separation, authority, refusal, recursion, recovery, and attestation. See the [candidate relationship record](../sf-amorph-data-drive/docs/ETABIT_RELATION.md).

## Evidence and next work

The immediate evidence comes from the archived **Decomposition / AE / Etabit successor handoff (2026-10-31)** and the underlying October 2026 user decisions. The next research task is a formal typed-reference contract separating source symbols, reference-resolution outcomes, operational faults, and effect authority; keep constructor/reader access boundaries explicit. Do not introduce native execution or modify original historical source packages as part of this schema work.
