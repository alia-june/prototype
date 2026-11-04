<div align="center">

# Etabit Schema

### A reference-native, multi-drive construction model for Amorphous Experience External Memory

**Human-directed research · Explicit composition · Distributed authority · Holonic refusal · Evidence-first development**

![Research status](https://img.shields.io/badge/status-research--draft-orange)
![Schema](https://img.shields.io/badge/descriptor-v0.2-blue)
![Admission](https://img.shields.io/badge/admission-not--admitted-red)
![Runtime](https://img.shields.io/badge/runtime-not--implemented-lightgrey)

**[Architecture](#architecture-at-a-glance) · [The four-symbol example](#the-four-symbol-source-drive) · [Cypher authority](#cypher-disk-distributed-authority-within-itself) · [Schema & examples](#the-schema-project) · [Validation](#validation-and-how-to-run-it) · [Research roadmap](#research-roadmap-and-admission-gates)**

</div>

---

> **Project boundary:** Etabit Schema documents how a system *could be constructed and qualified*. It is not a working Etabit drive, a filesystem, an on-media bit layout, a cryptographic implementation, a native-code interpreter, or an operational authority controller. Both committed descriptor versions are marked `DRAFT_NOT_ADMITTED`.

## The idea

Conventional storage presentations tend to put a file, its location, its structure, its interpretation, and the mechanisms authorized to change it behind one convenient interface. **Etabit investigates what happens when those responsibilities are kept explicitly separate.**

In Etabit, a source drive can supply objects while other drives describe **references, assembly relationships, ordering, and reuse**. An object can participate in multiple constructions without its source representation necessarily changing. Construction can recur across drives, with no fixed number of drives and no required particle-to-atom-to-molecule hierarchy.

The system is designed around another separation: **being able to refer to an object is not the same as being allowed to interpret, disclose, modify, or execute it.** Optional constructor-only metadata, an internally distributed **Cypher Disk**, process-scoped codepages, and the right of holonic constituents to refuse cooperation address different parts of that problem.

The long-range relationship established for this research is:

| Name | Meaning | Role |
| --- | --- | --- |
| **AE-Cryptography** | **Amorphous Experience Cryptography** (`ae-cryptography`) | Overall research system |
| **AE-External-Memory** | **Amorphous Experience External Memory** (`ae-external-memory`) | External-memory architecture |
| **Etabit** | Etabit (project spelling) | Generalized multi-drive construction |
| **EO-Drive** | **Experience Orchestration Drive** (`eo-drive`) | Intended result of an Etabit construction |

These are **names and intended relationships**, not proof of cryptographic secrecy or of an implemented EO-Drive.

## What makes Etabit different?

Five separations define the research direction:

1. **Objects are not their physical locations.** Source representations, placement, references, and assembly records need distinct identities and provenance.
2. **Composition is not interpretation.** A reference or a codepage relationship does not, by itself, settle the semantic meaning of what it addresses.
3. **Interpretation is not authority.** Even a correct interpretation does not authorize reading restricted metadata, writing a drive, or executing software.
4. **Cooperation is not compulsory.** Holonic constituents can refuse or revoke participation; being referenced or structurally interlocked does not make consent automatic.
5. **Uncertainty is not failure.** Stored `Unknown` and `Error` symbols must not be confused with unresolved references or failed device operations.

These are *architectural commitments and research requirements*. Their representation in JSON Schema is not equivalent to tested enforcement.

## Architecture at a glance

```text
             AMORPHOUS EXPERIENCE CRYPTOGRAPHY
                       ae-cryptography
                              |
                AMORPHOUS EXPERIENCE EXTERNAL MEMORY
                      ae-external-memory
                              |
                       ETABIT CONSTRUCTION
                              |
             +----------------+----------------+
             |                                 |
      SOURCE DRIVES                     REFERENTIAL DRIVES
      arbitrary objects                 bitmap / relation /
      or typed symbols                  assembly descriptions
             |                                 |
             +---------------+-----------------+
                             |
                qualified construction
                             |
                     EXPERIENCE ORCHESTRATION
                          DRIVE (target)
                             |
                   admitted reader interface
                        NOT DEFINED YET

   OOB META DISKS (optional)         CYPHER DISK
   constructor-only semantics        authority distributed
   not reader-accessible             within itself
                  \                   /
                   \   governs how   /
                    CONSTRUCTOR / ACCESS BOUNDARIES

     Holonic cooperation/refusal applies to participating parts.
     Codepages do not confer authority or executable meaning.
```

This is a **conceptual relationship diagram**, not a prescribed topology, execution sequence, disk count, or live interface. The Cypher Disk's internal constituents and decision protocol are not yet specified. The arrows do not authorize operations.

### The participating components

| Component | Responsibility | Boundary that must survive |
| --- | --- | --- |
| **Source drive** | Supplies addressable objects or symbols | Objects need not be 64-bit atoms or limited to four symbols |
| **Referential / bitmap drive** | Describes associations or assemblies using references | Exact grammar, order, repetition, cycles, and bounds are not yet approved |
| **Out-of-band meta disk** | Optionally supplies semantics/context for an associated Etabit drive | Constructor-scoped access; **reader cannot access it** |
| **Constructor** | Assembles representations from admitted source/reference information | Cannot self-grant disclosure or write authority |
| **Cypher Disk** | Distributes and establishes authority decisions among its own constituents | Neither single-controller authority nor a particular voting protocol is assumed |
| **Etabit reader** | Retrieves admissible constructed representations | Cannot read the out-of-band meta disks |
| **Codepage / interpreter boundary** | Associates representations with process-specific interpretation | Translation or recognition does not grant execution rights |
| **EO-Drive** | Intended outcome of Etabit construction | No persistent EO-Drive format, working mount, or reader ABI has been established |

### The historical three-drive example is not the architecture's limit

The earlier **Etadisk** illustration used:

- **A:** scattered and potentially replicated values;
- **B:** location/key or bitmap references identifying those values;
- **C:** assembly references describing how higher constructs are formed.

That was a useful explanatory example. The later **Etabit** design explicitly generalizes beyond three physical disks, beyond 64-bit source values, and beyond any fixed composition ladder. A logical drive need not correspond one-to-one with a physical disk; the physical association itself remains part of the unresolved Cypher-governed contract.

## The four-symbol source drive

One proposed source drive contains four distinguishable objects:

| Stored source symbol | What it establishes | What it does **not** establish |
| --- | --- | --- |
| `1` | A source object represented as `1` | Universal truth, permission, or native executable meaning |
| `0` | A source object represented as `0` | A universal false condition or absence of data |
| `Error` | A stored object whose identity is `Error` | That a disk read or the processing operation failed |
| `Unknown` | A stored object whose identity is `Unknown` | That a reference failed to resolve or that an operation did not finish |

**These are source symbols, not an accepted four-valued logical calculus.** No source-symbol bit assignment, algebra, truth table, codepage, or propagation rule is settled by this proposal. Four symbols can form arbitrary sequences if ordering is later defined; that mathematical possibility does not imply four valid executable states.

### Value and operation status must have different types

```text
successful retrieval  --->  stored object: "Error"
failed I/O request     --->  operational failure (no successfully retrieved object)

successful retrieval  --->  stored object: "Unknown"
unresolved reference   --->  reference-resolution outcome, not a stored symbol
```

The contract must separately describe at least **what object was requested**, **what value was retrieved**, **whether the reference resolved**, and **whether the operation succeeded**. The concrete transport type is **not yet defined**. Neither `Error` nor `Unknown` is a substitute for an explicit, appropriately typed failure or uncertainty record.

### Why source drives cannot be reduced to the four-symbol example

Etabit supports the *concept* of heterogeneous, arbitrary-object source drives. The four-symbol drive is a focused specimen for testing identity and uncertainty boundaries. An ASCII symbol map, a larger object repertoire, or a strict raw substrate would require a **separately identified profile and admission decision**, not a reinterpretation of these four labels in place.

## Referential construction

A referential drive identifies relationships among source objects and/or other referenced constructs. Possible levels of description include particles, atoms, molecules, structures, documents and other constructs—but none of those categories is mandatory, universally ordered, or automatically semantically valid.

A future reference contract must answer questions such as:

| Question | Unresolved contract |
| --- | --- |
| **Identity** | What precisely identifies a drive, an object, an occurrence, a version, or a copy? |
| **Targeting** | How does a reference bind to a target across drives and contexts? |
| **Ordering** | Are order and multiplicity encoded by references, separate maps, or both? |
| **Repetition** | Can one object appear repeatedly without duplicating its source representation? |
| **Recursion** | Which forms of self-reference or cyclic construction are meaningful or prohibited? |
| **Failure** | What happens when a target is missing, inaccessible, refused, malformed, or stale? |
| **Interpretation** | Which component may assign semantics to a construction, and under what authority? |
| **Recovery** | How are partially known or damaged constructions represented without inventing missing content? |

**A reference is not a permission token.** A successfully resolved object still has to cross independent admission and disclosure boundaries before it can influence any consequential process.

## Out-of-band metadata: constructor-only semantics

**Each Etabit drive may have an optional associated out-of-band meta disk.** It can help an authorized constructor understand the drive's semantics and relations. It must not be directly accessible to the Etabit reader.

The distinction is intentionally sharp:

| Activity | Constructor | Etabit reader |
| --- | --- | --- |
| Access admitted source / referential data | Subject to separate authorization | Subject to separate authorization |
| Read an out-of-band meta disk | **Scoped, when authorized** | **Denied** |
| Interpret semantic metadata for construction | Within permitted construction scope | No direct metadata access |
| Copy constructor-only metadata to reader-visible output | Not implicitly authorized | Not applicable |
| Modify metadata / alter drive association | Cypher-governed, implementation undefined | No authority implied |

The JSON descriptor demonstrates the intended boundary:

```json
{
  "id": "meta:four-symbol",
  "for_drive": "drive:four-symbol",
  "constructor_access": "SCOPED_ONLY",
  "reader_access": "DENIED",
  "automatic_disclosure": false,
  "representation_status": "SENTINEL_UNRESOLVED"
}
```

This object is an **excerpt from the v0.2 example**, not an executable access-control rule. A real implementation must separately prevent direct reads, unauthorized reclassification, indirect disclosure through construction results, and bypass through other interfaces.

## Cypher Disk: distributed authority within itself

The **Cypher Disk** is **not a conventional centralized authority disk**. Authority is distributed **inside the Cypher Disk itself**, among constituents whose organization and cooperative decision procedure have not yet been chosen.

It collectively decides five domains:

| Domain | Decision responsibility |
| --- | --- |
| **Metadata format** | How out-of-band semantic metadata is represented |
| **Drive associations** | How sources, reference drives, and meta disks relate |
| **Constructor protocol** | Under which rules constructors may participate |
| **Disclosure controls** | What information can cross which boundaries |
| **Write authority** | Who or what may change protected state, and under which rules |

**No precedence exists among these five just because they appear in a list.** v0.2 intentionally expresses them as an unordered five-member set, correcting an accidental array-order constraint in v0.1.

The design may admit a **ceramic mechanical** Cypher construction. That is a user-proposed physical possibility, **not a selected mechanism or an implemented material/engineering specification**.

The following are explicitly open: constituent number and identities; physical topology; collective decision rules; thresholds or veto conditions; refusal handling; persistent authority records; recovery; and independently demonstrable enforcement. Do not infer majority voting, secret sharing, key schedules, a single trusted controller, or cryptographic security from the name *Cypher* alone.

## Holonic cooperation and the right to refuse

Etabit is intended to support holonic compositions in which constituents retain the ability to **deny cooperation**. Cooperation can be conditional, narrow, and revocable. Neither a stored reference nor a locked/interlocking relationship inherently obliges a constituent to participate.

```text
reference       != binding
binding         != consent
consent         != permanent permission
capability      != authority
refusal         != global system failure
```

A constituent's refusal cannot be bypassed merely because an alternative path is technically available. Another eligible construction may be considered **only if it does not appropriate the refusing constituent's resources, permissions, or protected information**.

For the Cypher Disk, this creates an open problem: how does an internally distributed authority reach an admissible decision when a constituent refuses cooperation? The protocol is not yet specified, and this repository does **not** assume unanimity, quorum, majority, or a universal veto.

## Codepages, language boundaries, and UNSF

Etabit's source representations are not automatically native program code. A source or referential drive may be associated with a **process-specific codepage**, and codepages themselves may refer to separate referential drives.

The research includes a **disabled, non-executing interpretation profile**, intended to prevent a representation from automatically acquiring an executable meaning merely because a host compiler or process recognizes some of its bytes.

That is an *intended admission model*, **not a claim that encoding alone guarantees non-execution**. Conversion, interpretation, permissions and effects require separate gating and evaluation.

The current name **`UNSF`** supersedes historical **`USF`**. Preserve older source labels where needed for provenance; do not silently rewrite historical artifacts or invent an expansion of `UNSF`.

## The schema project

This repository supplies **research descriptors**: JSON documents that record proposed parts, relationships, design decisions and unresolved contracts. These are **not** physical storage layouts or runnable devices.

### Repository map

```text
etabit-schema/
├── README.md
├── schema/
│   ├── etabit-project.schema.json          # v0.1: preserved initial descriptor
│   └── etabit-project.v0.2.schema.json     # v0.2: expanded research descriptor
├── examples/
│   ├── four-symbol-source.json             # v0.1 specimen
│   └── four-symbol-source.v0.2.json        # v0.2 specimen
├── docs/
│   ├── DECISIONS.md                        # decisions, sources, open contracts
│   └── V0_2_AUDIT_RECONCILIATION.md        # traceability and limitations
└── tests/
    └── test_v0_2.py                       # optional descriptor/graph checks
```

| Artifact | Read it for |
| --- | --- |
| **[v0.2 schema](schema/etabit-project.v0.2.schema.json)** | Current exploratory descriptor fields and constant design boundaries |
| **[v0.2 four-symbol specimen](examples/four-symbol-source.v0.2.json)** | A concrete illustrative source drive, a reference, meta disk and codepage relationship |
| **[Audit reconciliation](docs/V0_2_AUDIT_RECONCILIATION.md)** | Which v0.1 gaps were addressed and which proof obligations remain |
| **[Decision ledger](docs/DECISIONS.md)** | User-originated instructions vs derived analytical proposals and unresolved choices |
| **[Validation script](tests/test_v0_2.py)** | Schema-shape and candidate in-document graph checks |
| **[v0.1 schema](schema/etabit-project.schema.json)** / **[v0.1 specimen](examples/four-symbol-source.json)** | Historical initial research baseline, preserved unchanged |

### What changed between v0.1 and v0.2?

| Area | v0.1 | v0.2 |
| --- | --- | --- |
| Drives | `kind` and broadly descriptive source-symbol lists | `roles`, separately declared object identities and payload *descriptors* |
| References | Free-form relationship with grammar status | Explicit source/target IDs plus separate grammar, ordering, multiplicity and cycle statuses |
| Codepages | Process namespace and mapping/execution semantics | Explicit codepage-to-referential-drive IDs and translation-admission status |
| Cypher responsibilities | Five items accidentally in a fixed array order | Five unique **unordered** required responsibilities |
| Cypher constituents | Not structurally described | Candidate constituent descriptions; actual membership/protocol still unresolved |
| Holonic refusal | Refusal requirement and open protocol | Separate descriptive refusal and revocation status fields |
| Result boundaries | Basic distinctions declared | Dedicated section separating stored symbols from operational result categories |
| Admission | `DRAFT_NOT_ADMITTED` | `DRAFT_NOT_ADMITTED` |

**v0.2 does not supersede v0.1 as accepted canon.** It is a separately versioned research candidate; v0.1 remains intact for comparison.

### Reading the v0.2 example

The example declares three illustrative drives: a four-symbol source, a referential construction drive, and a codepage-associated referential drive. It includes one declared reference to `symbol:1`, one optional-style metadata specimen, and a codepage pointing to a referential drive. The Cypher constituents array is empty **because membership has not been specified**, not because the design requires zero constituents.

Values such as `SENTINEL_UNRESOLVED` and `SENTINEL_UNASSIGNED` are **explicit unresolved states**. They are not values the reader may treat as zero, false, a grant, or empty content.

The schema does **not** use JSON `null` for unresolved fields. An empty array in an example means only that **no entries are recorded in that descriptor**; it does not prove that such constituents or objects do not exist.

## Validation and how to run it

From the repository root, with Python and the third-party `jsonschema` package installed:

```bash
python -m pip install jsonschema
python etabit-schema/tests/test_v0_2.py
```

Or from this directory:

```bash
python -m pip install jsonschema
python tests/test_v0_2.py
```

The supplied test program is designed to check:

- validity of the v0.2 example under **JSON Schema Draft 2020-12**;
- local reference endpoints and codepage-to-referential-drive associations;
- rejection of forbidden descriptor settings such as reader metadata access, implicit disclosure, codepage execution permission and refusal bypass;
- rejection of missing, extra or duplicate Cypher responsibilities;
- acceptance of a **different ordering** of the same five responsibilities.

**Test boundary:** This script is an offline document and local-graph validator. It does not mount or write drives, activate codepages, exercise constructor or reader implementations, prove information-flow isolation, establish collective Cypher authority, or attest cryptographic properties. Test presence must not be confused with an independently executed and verified test result.

### A passing schema is not a secure system

A JSON Schema validator can validate **shape and declared invariants**; even the additional local graph checker cannot prove real-world enforcement. For example, a field containing `"reader_access": "DENIED"` describes a required boundary. It does **not** prevent a real process from opening a device.

Further, the schema `$id` currently points to a file on the moving `main` branch; consumers requiring reproducible evidence should pin a commit or tagged release rather than treating that URL as an immutable publication.

## Relationship to other prototype projects

### [Syn-Etabit Transformer — Textual](../syn-etabit-transformer-textual/README.md)

A separate reference-native **document transformation** project, with an existing bounded CPU model, map construction, identity, context/selection ideas and its own evidence and testing. It studies document structure and transformation, **not an already deployed general Etabit storage substrate**.

Its safe-ASCII 128-symbol construction is distinct from the four-symbol drive specimen here; neither automatically supersedes the other, and no general cross-encoding has been approved.

### [sf-AmorphDataDrive / sf-Edabit](../sf-amorph-data-drive/README.md)

A separate raw-substrate architecture with a **locked v0.3 baseline** and the conceptual progression:

```text
D0 = existence
D1 = relation / interpretation
D2 = composition / coherence
```

In particular, **D0 stays raw, flat, ordered, and enumerated**. Identity, metadata, datatype, encoding, attestation, reconstruction, filesystem and composition are **outside D0**. Etabit's arbitrary-object source-drive concept does not rewrite that lock.

A future Etabit source/substrate relationship is **candidate only**, requiring an independently reviewed identity/reference/authority/recovery cross-map. Consult [the explicit Etabit relationship record](../sf-amorph-data-drive/docs/ETABIT_RELATION.md) before attempting integration.

## Research roadmap and admission gates

This is a **qualification sequence**, not a claimed implementation schedule.

| Gate | Work | Evidence required before promotion |
| --- | --- | --- |
| **R0 — Source fidelity** | Reconcile user instructions, historical Etadisk evidence, updated AE/EO names, and schema history | Provenance register with clear direct/derived/unknown labels |
| **R1 — Minimal typed model** | Define objects, references, read results, identity and unresolved/error distinctions in a CPU-only reference model | Deterministic contracts, independent oracle and exhaustive/negative tests on small domains |
| **R2 — Composition** | Define ordering, multiplicity, recursion, version/generation and reference consistency | Malformed graph tests, boundary/property tests, replay and provenance preservation |
| **R3 — Cooperation** | Specify consent, refusal, revocation and alternate qualified construction | Tests proving non-bypass, bounded operation and no authority escalation |
| **R4 — Metadata isolation** | Specify constructor OOB access and reader nonaccess, including indirect disclosure channels | Demonstrable separation and negative information-flow tests |
| **R5 — Cypher decisions** | Develop and evaluate a distributed internal decision protocol, without assuming topology | Independently checked authority/partition/failure/recovery behavior |
| **R6 — Persistence and recovery** | Specify EO-Drive format, writes, commits, partial failures, crash recovery and reader interface | Durable replay, corruption detection, bounded recovery and independent qualification |
| **R7 — Specialized realization** | Evaluate possible electronic, mechanical or mixed implementations and optional accelerated paths | Parity with reference semantics, physical enforcement evidence and explicit operator admission |

The earlier user's correctness-first direction remains important here: **do not make voxel kernels, GPU acceleration, filesystem filters, native execution or autonomous orchestration prerequisites for a correct reference model**.

### Core non-collapse rules

- **Stored value ≠ read outcome ≠ reference outcome ≠ execution status.**
- **Reference ≠ semantic interpretation ≠ disclosure permission.**
- **Codepage recognition ≠ executable authority.**
- **Constructor knowledge ≠ reader entitlement.**
- **Cypher decision description ≠ physical enforcement.**
- **Holonic association ≠ irrevocable cooperation.**
- **Schema validity ≠ deployed safety, secrecy, or recovery.**

## Provenance, status and contribution discipline

The design originated through a sequence of user-supplied directions and corrections; analytical reconciliations, machine-readable examples and verification proposals are **derived work** and are not automatically canonical. In particular:

- **Historical name:** Etadisk; its three-drive A/B/C illustration remains evidence of an earlier formulation.
- **Later construction direction:** Etabit as heterogeneous multi-drive referential construction, with the four-symbol source as one specimen.
- **Authority corrections:** Constructor-only optional metadata; Cypher authority distributed *within itself*; holonic cooperation can be refused.
- **Current system names:** AE = **Amorphous Experience**; EO = **Experience Orchestration**; `UNSF` supersedes the earlier `USF` label.
- **Schema revisions:** v0.1 and v0.2 are documented, source-scoped **research candidates**, not accepted formats.

When proposing additions, distinguish **direct user decision**, **historical evidence**, **derived interpretation**, **implemented/tested behavior**, **unverified claim**, and **unresolved contract**. Preserve superseded versions rather than silently rewriting history. Do not assign numerical bitcodes, collective decision rules, source alphabets, or machine permissions solely to make a document appear complete.

For current work, begin with the [decision ledger](docs/DECISIONS.md) and [v0.2 audit reconciliation](docs/V0_2_AUDIT_RECONCILIATION.md). Then change one bounded contract at a time, with its independent negative tests and evidence limits.

---

<div align="center">

**Make construction inspectable. Keep meaning separate from representation, and authority separate from both.**

*Etabit Schema — research descriptor v0.2 · Not admitted · No active storage or execution authority*

</div>
