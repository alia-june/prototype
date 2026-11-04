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

## How to use

Inspect the schema and example as **data**, not instructions. They describe the intended boundaries but do not enforce them. A JSON Schema validator can check a descriptor's declared shape and fixed values; it **cannot** certify disk access isolation, physical layout, Cypher collective decisions, safe execution, or cryptographic security.

No numeric codepage IDs, Etabit bitcodes, byte layouts, physical addressing, voting protocols or active authority are assigned here.

## Relation to Syn-Etabit Transformer — Textual

[Syn-Etabit Transformer — Textual](../syn-etabit-transformer-textual/README.md) already documents a reference-addressed document/map model and a bounded CPU implementation. This schema project is **separate** and describes the wider Etabit drive architecture. The related implementation is not evidence of a deployed general Etabit drive, an `eo-drive`, or a Cypher Disk.

## Evidence and next work

The immediate evidence comes from the archived **Decomposition / AE / Etabit successor handoff (2026-10-31)** and the underlying October 2026 user decisions. The next research task is a formal typed-reference contract separating source symbols, reference-resolution outcomes, operational faults, and effect authority; keep constructor/reader access boundaries explicit. Do not introduce native execution or modify original historical source packages as part of this schema work.
