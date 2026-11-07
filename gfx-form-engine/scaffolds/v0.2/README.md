# GFX Form Engine / Encoded Lexical Raster — Scaffold v0.2

CPU-compilable scaffold for the current GFX Form Engine architecture, with HIP integration kept behind an explicit unvalidated backend boundary.

## Current implemented substrate

- Abstraction / Abstract Form markers (no active `META` vocabulary)
- Atomics: `Identity`, `Code`, `Value`, `Mask`
- Binding, Relation, first-class Reference
- Validation, Provenance, Composition / Decomposition
- Activation, Continuation, Progress, first-class Recursion
- Recursion governor with **no universal fixed depth limit**
- Generic frame-scoped XYZ coordinates
- Frame / frame-mapping records
- Generic sparse `Plane<T>`
- Backing classes and bindings
- Voxel as a composite structure, not a root primitive
- Execution matrix scaffold
- One 3D cast + aligned Plane 1/2/3 result model
- CPU recovery authority interface
- Encoded Lexical Raster storage
- JSON-0 CPU lexical reference pass: classification, escape/string state, structural mask, depth field, structural compaction
- CPU tests
- HIP backend boundary stub

## Plane semantics

1. **Plane 1** — preferred direction / form intent
2. **Plane 2** — admissible / authorized possibilities
3. **Plane 3** — exception, recovery, fallback, recursion governance

A single cast may resolve a 3D location, then all planes are read at that aligned frame/coordinate. Plane 3 supplies recovery availability, but CPU recovery authority remains canonical.

## Coordinate semantics

`x`, `y`, and `z` have no permanent global meaning. Meaning is supplied by the active `Frame` and its relation schema.

## JSON-0

The CPU reference implementation currently proves the first ELR concept:

```text
immutable source concept
  → lexical classification
  → escape state
  → string state
  → structural mask
  → depth field
  → compact structural positions
```

It is not yet a complete RFC 8259 parser. UTF-8 validation, exact number/literal grammar, matched opener/closer typing, spans, node relationships, sequencing records, and GPU kernels remain TODO.

## Build

```bash
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure
```

## Target

Primary intended hardware/runtime target remains Windows 11 x86-64 + AMD Radeon RX 7700 XT + AMD HIP SDK. This scaffold does not claim HIP behavior that has not been validated on that machine.
