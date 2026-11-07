# GFX Form Engine / Encoded Lexical Raster — Scaffold v0.9

CPU-compilable C++20 scaffold for the current GFX Form Engine architecture. HIP and Windows worker paths remain explicit unvalidated boundaries.

## Implemented substrate

- Abstraction / Abstract Forms; no active `META` vocabulary.
- Atomics: `Identity`, `Code`, `Value`, `Mask`.
- Binding, Relation, first-class Reference, Validation, Provenance, Composition / Decomposition.
- Activation, Continuation, Progress, first-class Recursion with no universal fixed depth cap.
- Explicit `ActivationGraph`, generation-scoped `ContinuationChain`, and `RecoveryDomain` scoping.
- Canonical `ExecutionEnvelope`: INTENT → PRECHECK → EFFECT → COMPLETE → COMMIT, with FAULT diversion.
- Bounded execution `BreadcrumbRing`, semantic worker heartbeat, and fault-capsule contract.
- Transaction ledger plus both structural `CommitCertificate` continuity and SHA-256-backed `IntegrityCommitCertificate` chaining. SHA-256 provides tamper-evident integrity, not signer authenticity.
- Recovery checkpoint selection, restore planning, and composed RecoveryPlan validation across checkpoint + route + RecoveryDomain; planning/validation never grants recovery authority.
- Cross-frame tri-plane casts execute only through explicit validated frame-mapping paths.
- JSON source mutation plans are generation-bound, reject overlaps/stale generations, create a new source generation, and request ELR rebuild rather than mutating derived planes in place.
- Generic frame-scoped XYZ coordinates, reversible mappings, explicit semantic projections, frame graphs and mapping-chain execution.
- Generic `Plane<T>`, descriptors, dense/sparse/brick backing scaffolds and homogeneous typed backing pools.
- Generation/epoch-scoped `AlignedPlaneIndex` for one-location aligned Plane 1/2/3 lookup.
- Route / RouteStep molecules and explicit Matrix→Route bindings.
- One 3D cast followed by aligned Plane 1/2/3 reads.
- Plane 1 direction/form intent; Plane 2 admissible possibilities; Plane 3 recovery/fallback + recursion governance.
- Recovery-route lookup, explicit recovery authorization, PREPARE→COMMIT route transaction semantics and recovery checkpoints.
- Voxel remains a composite structure, not a primitive root.
- Encoded Lexical Raster with explicit plane descriptors and explicit stage/generation lineage.
- Generic local-coordinate `FormFragment<T>` plus initial JSON lexical fragments/form recognition.
- JSON-0 iterative CPU parser with UTF-8, number grammar, escape/string validation, Unicode surrogate pairs, structural balance/type matching, spans, nodes, sequencing and explicit Relations.
- JSON members have complete spans plus explicit MemberKey / MemberValue relations.
- JSON retains the authoritative source text and supports exact source reconstruction plus parse/reparse round-trip validation.
- JSON-0 emits first-class Reference/Provenance lineage for source and derived parse products.
- DDA voxel-step primitive, cast trace, transaction ledger and sentinels.
- HIP backend and Windows supervisor interfaces remain stubs until target-machine validation.

## Core construction

```text
ABSTRACTION
  → ABSTRACT FORMS
  → CONCRETE SCHEMAS
  → ATOMICS
  → MOLECULES
  → STRUCTURES
```

`Generic` and `Polymorphic` are schema/realization modifiers. They do not create hidden semantics.

## Tri-plane model

```text
one 3D cast → frame-scoped coordinate
                   │
                   ├─ Plane 1: direction/form intent
                   ├─ Plane 2: admissible/authorized possibilities
                   └─ Plane 3: recovery/fallback/recursion governance
```

The three reads align on frame, coordinate, generation and execution context. Plane 3 provides recovery availability, not autonomous recovery authority.

## JSON-0 / ELR

```text
immutable source
  → lexical classification
  → escape state
  → string state
  → structural mask
  → depth field
  → structural compaction
  → spans / nodes / Relations / sequencing / forms
  → exact-source reconstruction / round-trip validation
```

The parser is iterative and retains the 5,000-level nesting test without native recursive descent.

## Build

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

## Target

Primary intended target remains Windows 11 x86-64 + AMD Radeon RX 7700 XT + AMD HIP SDK. This scaffold does not claim target-GPU or Win32 supervisor behavior that has not been run on that machine.

## v0.9 status

Clean C++20 build and **38/38 CPU tests pass**. See `docs/BUILD_REPORT_v0.9.md` and `logs/` for current provenance, decisions, experiments, assumptions, errors and TODOs.
