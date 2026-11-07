# Canonical Architecture Snapshot

## Construction hierarchy

```text
ABSTRACTION
│
├── ABSTRACT FORMS
│   ├── Atomic Form
│   │   └── Primitive
│   └── Molecular Forms
│       ├── Binding
│       ├── Relation
│       ├── Reference
│       ├── Validation
│       ├── Provenance
│       ├── Composition
│       ├── Decomposition
│       ├── Activation
│       ├── Continuation
│       ├── Progress
│       └── Recursion
│
├── MODIFIERS
│   ├── Generic
│   └── Polymorphic
│
↓
CONCRETE SCHEMAS
↓
ATOMICS
↓
MOLECULES
↓
STRUCTURES
```

Large structures including Voxel, Frame, Plane, ELR, Cast, Matrix, Route, RecoverySet, JSON structures and protocol structures are compositions, not primitive roots.

## Atomic rule

An Atomic carries one irreducible typed fact. Initial logical families:

- IDENTITY
- CODE
- VALUE
- MASK

No molecule may introduce hidden semantics not recoverable from constituent atomics, relations, references, and explicit operations.

## Reference

Reference is first-class, typed, generation-aware, scope/frame-aware, authority-aware, resolvable and validatable. Raw native pointers never substitute for persistent References.

## Recursion

Recursion is first-class and explicit through Reference + Activation + Continuation + Progress + Recovery binding. Native call-stack recursion is not authoritative architecture state.

No universal fixed depth limit. Recursion is dynamically governed by progress, resource, cycle, continuation, generation and sentinel invariants. Plane 3 is the recursion governor.

## Coordinate / Frame

X/Y/Z are generic coordinate functions with no permanent semantics. A Frame gives semantic meaning through axis functions, domains, orientation, relations, mappings and generation.

A coordinate is semantically incomplete without a frame.

Coordinate transforms preserve represented identity; semantic projections may alter/discard meaning and therefore require explicit operation, provenance, loss declaration and validation.

## Encoded Lexical Raster

ELR is a coordinate-addressed lexical representation.

- authoritative immutable source bytes
- visible/palette-coded lexical raster
- dense backing planes for common per-position attributes
- sparse backing planes/indexes for expensive/infrequent attributes
- all derived planes carry generation/provenance/validation
- logical 3D views need not be dense physical 3D storage

Core pattern:

```text
SOURCE
 ↓
DENSE ELR
 ↓
mask / combine / scan
 ↓
COMPACT
 ↓
SPARSE STRUCTURAL INDEX
 ↓
MOLECULES / FIVE STREAMS
```

## Tri-plane cast

One cast may resolve one 3D location in a shared Frame. Aligned plane reads occur at that same coordinate.

- Plane 1: direction/form intent
- Plane 2: admissible/authorized possibilities
- Plane 3: exception/recovery/fallback and recursion governance

Plane 1 proposes. Plane 2 authorizes. Plane 3 supplies bounded fallback/recovery availability. Plane 3 does not self-authorize restoration; CPU recovery authority remains canonical.

## Physical representation

Logical polymorphism may resolve to dense, sparse, brick, CPU, or GPU backing. Prefer homogeneous physical backing pools for GPU locality. Sparse/tiled/bricked storage is preferred for large logical voxel spaces unless measurement proves otherwise.

## JSON-0

JSON is the first canonical workload.

Passes:
1. Admit source
2. Classify bytes
3. Validate UTF-8
4. Resolve escapes
5. Resolve quotes/strings
6. Build structural index
7. Resolve nesting
8. Discover value spans
9. Classify/validate values
10. Build relationships
11. Build sequencing
12. Cross-validate
13. Commit parse generation

Source bytes remain immutable and authoritative.
