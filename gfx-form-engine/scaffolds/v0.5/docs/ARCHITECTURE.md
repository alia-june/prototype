# Architecture Canon — v0.5

## Construction

```text
ABSTRACTION
  → ABSTRACT FORMS
  → CONCRETE SCHEMAS
  → ATOMICS
  → MOLECULES
  → STRUCTURES
```

Large constructs such as Voxel, Frame, Plane, ELR, Cast, Matrix, Route, RecoverySet, and JSON document structure are compositions, not primitive roots.

## Atomics
Initial logical families: IDENTITY, CODE, VALUE, MASK. Exact machine bitcodes and packed binary layouts remain unfrozen.

## Reference
Reference is a first-class molecular form with identity, source, target, kind, scope/frame, expected generation, authority, resolution state, and validation state. Persistent contracts never depend on raw native pointers.

## Recursion
Recursion is explicit through Reference + Activation + Continuation + Progress + Recovery binding. There is no universal fixed depth limit. Plane 3 dynamically governs progress, resources, cycles, continuations, sentinels, checkpoints and fallback.

## Generic coordinates and frames
X/Y/Z are generic coordinate functions. Meaning is supplied by the active Frame and relations among axes. A coordinate is semantically incomplete without its Frame. Reversible coordinate transforms are distinct from semantic projections.

## ELR
Encoded Lexical Raster preserves immutable source authority and derives aligned lexical/backing planes. Plane descriptors carry identity, kind, storage class, generations, element count/width and validation mask. Dense operations discover form; sparse molecular/index structures carry higher-level structure.

## Tri-plane casting
One cast resolves one frame-scoped 3D coordinate. Plane 1 proposes direction/form intent. Plane 2 defines admissible possibilities. Plane 3 supplies exception/recovery/fallback and recursion governance. Recovery routes may be prebound to Plane 3 options, but CPU recovery authority must explicitly authorize restoration/reauthorization.

## Polymorphic backing
Logical polymorphism resolves to typed homogeneous backing pools and dense/sparse/brick implementations. The core avoids arbitrary pointer graphs.

## Routes
RouteStep is a molecular edge between frame-scoped CoordinateAddresses with explicit operation/state/continuation data. Route validates chain continuity, frame and generation. Recovery routes reuse the same route molecule under recovery-specific authority.

## JSON-0
The CPU oracle is iterative, not native-recursive. It builds ELR lexical state, validates UTF-8 and JSON number grammar, creates spans/data/nodes/sequencing, emits explicit generic Relation records, and cross-validates relations and sequence linkage.
