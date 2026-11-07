# GFX Form Engine / Encoded Lexical Raster — Scaffold v0.5

CPU-compilable scaffold for the current GFX Form Engine architecture. HIP and Windows worker paths remain explicit unvalidated boundaries.

## Implemented substrate

- Abstraction / Abstract Forms; no active `META` vocabulary.
- Atomics: `Identity`, `Code`, `Value`, `Mask`.
- Binding, Relation, first-class Reference, Validation, Provenance, Composition / Decomposition.
- Activation, Continuation, Progress, first-class Recursion.
- Recursion governance with no universal fixed depth cap.
- Generic frame-scoped XYZ coordinates and reversible frame mappings / explicit semantic projections.
- Frame graph with validated multi-edge path discovery.
- Generic sparse `Plane<T>` with plane descriptors and typed backing bindings.
- Homogeneous backing pools for logical polymorphism without pointer-oriented object graphs.
- Dense / sparse / brick backing scaffolds.
- Route and RouteStep molecules.
- One 3D cast followed by aligned Plane 1/2/3 reads.
- Plane 1 direction/form intent; Plane 2 admissible possibilities; Plane 3 recovery/fallback + recursion governance.
- Recovery candidates may identify prebuilt recovery routes, but CPU recovery authority remains canonical.
- Voxel remains a composite structure, not a primitive root.
- Encoded Lexical Raster with explicit plane descriptors.
- JSON-0 iterative CPU parser: UTF-8, number grammar, strings/escapes, structural balance/type matching, spans, nodes, sequencing, explicit Relations.
- JSON relationship and sequence cross-validation.
- DDA voxel-step primitive, sparse brick scaffold, cast trace, transaction ledger, sentinels.
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

The three reads must align on frame, coordinate, generation and execution context. Plane 3 provides recovery availability, not autonomous recovery authority.

## JSON-0 / ELR

```text
immutable source
  → lexical classification
  → escape state
  → string state
  → structural mask
  → depth field
  → structural compaction
  → spans / nodes / Relations / sequencing
```

The parser is iterative and passes a 5,000-level nesting test without native recursive descent.

## Build

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

## Target

Primary intended target remains Windows 11 x86-64 + AMD Radeon RX 7700 XT + AMD HIP SDK. This scaffold does not claim target-GPU or Win32 supervisor behavior that has not been run on that machine.

## v0.5 status

v0.5 adds homogeneous typed backing pools, Plane descriptors, Route/RouteStep molecules, recovery-route lookup, frame-graph path traversal, explicit ELR plane descriptors, and explicit JSON Relations with cross-validation. The CPU build passes **16/16 tests**.
