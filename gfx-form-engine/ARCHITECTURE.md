# GFX Form Engine Architecture

GFX Form Engine represents structure, execution, and recovery as explicit data. A frame defines what coordinates mean. A cast locates a candidate in that frame. Three aligned reads describe the intended action, the admissible possibilities, and the available recovery options. Execution and recovery use their own records and authority checks.

This document describes the architecture and its realization in the **v0.9 C++20 scaffold**. JSON-0 is the first concrete workload. Configurable voxel signaling and neural-engine compositions are research directions.

## 1. Forms and composition

```text
Abstraction → Abstract Forms → Concrete Schemas → Atomics → Molecules → Structures
```

**Primitive** is the Abstract Form that produces Atomics through concrete primitive schemas. An Atomic expresses one typed fact. The initial families are **Identity**, **Code**, **Value**, and **Mask**. The scaffold has working representations for these families; their existence does not freeze machine bitcodes or packed layouts. Generic and Polymorphic describe how schemas or realizations can vary.

| Form | Responsibility |
| --- | --- |
| Binding | Associates a subject with a value or object in a declared role. |
| Relation | Describes how identified things are connected, such as containment or sequence. |
| Reference | Identifies a target together with the context needed to resolve it, such as the expected generation. It is a first-class form. |
| Validation | Records checks and their results for a declared scope. |
| Provenance | Records the source and derivation of a fact or structure. |

These forms give the engine a way to express a binding, describe its relationships, resolve its references, validate the result, and retain its origin. They are reusable building blocks; an operation can use the subset it needs. Frames, planes, voxels, routes, and recovery structures are compositions. The scaffold's composition comparison checks identity sets, so it does not establish ordering, multiplicity, or behavioral equivalence.

## 2. Frames, casts, and aligned reads

XYZ has no permanent meaning across GFX. The **active frame** defines the interpretation of its coordinates. A frame mapping changes the coordinate representation; the scaffold supports reversible reindexing by axis permutation, sign change, and offset. A semantic projection instead declares which relations it retains or discards and records loss and provenance. A change to network connections or parameter bindings would change the composition itself.

```text
One 3D cast → one frame-scoped location
                 ├─ Plane 1: proposed direction or form intent
                 ├─ Plane 2: admissible possibilities
                 └─ Plane 3: fallback, recovery, and recursion governance
```

The reads use the same location in the same frame and generation. In the v0.9 cross-frame scaffold, an existing source address is mapped through an explicit frame path before the aligned reads. This composes mapping and resolution; it is not a complete spatial ray search. Plane 3 can supply a recovery candidate. CPU authority determines whether a recovery action may proceed.

Spatial discovery, signal delivery, and activation are distinct operations. A cast can locate a candidate without traversing neural links; proximity does not establish a link, and locating a candidate does not grant authority to deliver a signal or start work.

## 3. Execution, recursion, and recovery

**Activation** identifies an instance of work and can record its parent. **Continuation** represents suspended work explicitly. **Progress** describes how an execution regime recognizes forward movement. **Recursion** is a first-class form whose state can be tracked independently of native stack depth.

The scaffold's execution envelope advances through `INTENT → PRECHECK → EFFECT → COMPLETE → COMMIT`, with `FAULT` as an explicit diversion before commitment. The envelope checks phase order. Routes describe proposed operations and addresses; a route's transaction ledger separately represents `PREPARE` and `COMMIT`. The phase envelope and the ledger answer different questions: where work is in its lifecycle, and what commitment evidence exists for it.

Plane 3 governs recursion recovery without a universal depth cap. The scaffold monitors regime-supplied progress measures, repeated state tokens, and resource use. A workload may need to distinguish waiting or productive recurrence from a stall; it must supply observations that make that distinction meaningful. A bounded breadcrumb history limits retained evidence, not recursion depth.

A **Recovery Domain** groups activations, routes, and backing objects that may share a recovery outcome. A checkpoint identifies a possible resumption point. In v0.9 a composed recovery plan checks checkpoint, route, domain, frame, transaction, generation, and membership before returning `AuthorizationRequired`. The separate authorization step matches the supplied approval against the transaction, route, and generation. A validated plan is a candidate; recovery execution and restoration of live state are separate integration work.

The scaffold carries two kinds of commitment evidence: a structural predecessor chain and a SHA-256 digest-linked certificate chain. The latter includes a supplied payload digest. Neither establishes signer authenticity, durable persistence, or crash consistency. Heartbeats, breadcrumbs, and fault capsules provide execution evidence; they do not authorize a transition.

## 4. Worked example: JSON-0 and ELR

Consider source identity `5`, generation `1`, with this retained text:

```json
{"a":1,"b":2}
```

1. **Classify the source.** The Encoded Lexical Raster records byte classes, escape and string state, structural positions, and nesting depth. Structural positions can be compacted for subsequent processing.
2. **Build structure.** The iterative CPU parser derives spans, nodes, data elements, relations, and sequencing. A member's key and value are related explicitly. A source Reference identifies the authoritative generation; Provenance connects derived records back to it.
3. **Recover the exact text.** Reconstruction returns retained source text, preserving whitespace and escapes. The scaffold's reparse comparison checks validity, source equality, and selected record counts. It is a bounded repeatability check, rather than a complete comparison of every derived field.
4. **Propose a new generation.** A mutation plan can replace the `1` at byte offset `5` with `99`. The plan names the source, expected generation `1`, and target generation `2`. It checks generation, bounds, and overlapping ranges, builds new text, and reparses it. The earlier document remains available. A separate ELR rebuild request identifies the derived view that needs regeneration against generation `2`.

This example illustrates how Reference and Provenance preserve source identity across change. The same pattern is worth investigating for construction changes in voxel assemblies, where cached views may also need to be regenerated.

## 5. Research extensions and validation boundaries

The voxel research asks whether a voxel can host a neural engine with a limited number of declared inputs and outputs, with shared or specialized parameters. Port count, traffic rate, buffer capacity, and execution budget are separate design choices. A composition could report its current construction so a configurable cast can be directed against the right generation. A voxel's *sensorium* could combine passive observation and active probing, including observations of engines with which it has no neural connection. Carbon-inspired and buckyball-like assemblies remain topology research; their geometry does not prescribe an engine's port count.

The [v0.9 build report](scaffolds/v0.9/docs/BUILD_REPORT_v0.9.md) records **38/38 CPU tests passing**, including the 5,000-level iterative JSON nesting case. This is the package's reported result. HIP execution and performance on the intended Windows 11 / Radeon RX 7700 XT target, Windows worker supervision, and durable commit behavior remain outside that validation.

See [README.md](README.md) for theoretical uses and CPU build instructions, and the [Decision Ledger](scaffolds/v0.9/logs/DECISION_LEDGER.md) for the scaffold's design record.
