# Architecture Canon

## Construction

```text
ABSTRACTION
  → ABSTRACT FORMS
  → CONCRETE SCHEMAS
  → ATOMICS
  → MOLECULES
  → STRUCTURES
```

`Generic` and `Polymorphic` modify schemas/realization without silently adding semantics.

## Atomics
Initial logical families: IDENTITY, CODE, VALUE, MASK. Exact machine bitcodes remain unfrozen.

## First-class Reference
References are explicit typed objects with target identity, frame/scope, expected generation, authority, resolution and validation state. Persistent contracts do not use raw native pointers.

## First-class Recursion
Recursion is explicit through Reference + Activation + Continuation + Progress + Recovery binding. Depth is observed but is not a universal safety bound. Plane 3 governs dynamic recursion safety.

## ELR
Encoded Lexical Raster uses an immutable authoritative source concept and derived backing planes. Dense operations discover form; sparse compaction carries higher-level structure.

## Tri-plane casting
One 3D cast resolves a coordinate; aligned plane reads at that coordinate provide direction, possibilities, and recovery/fallback. The coordinate is frame-scoped.
