# GFX Form Engine / Encoded Lexical Raster — Architecture v0.6

## Construction

```text
ABSTRACTION
  → ABSTRACT FORMS
  → CONCRETE SCHEMAS
  → ATOMICS
  → MOLECULES
  → STRUCTURES
```

`Generic` parameterizes schemas. `Polymorphic` selects compatible realization. Neither creates hidden semantics.

Large structures (`Voxel`, `Frame`, `Plane`, `ELR`, `Cast`, `Matrix`, `Route`, recovery structures, JSON structures) remain compositions rather than primitive roots.

## First-class Reference and Recursion

Reference is explicit, typed, generation/scope/frame/authority aware, resolvable and validatable. Recursion is explicit through Reference + Activation + Continuation + Progress + Plane-3 recovery state. There is no universal recursion-depth ceiling; progress/resources/cycles/continuations/sentinels govern continuation.

Recovery checkpoints may preserve recursion activation, coordinate, transaction, generation, progress and validation state for fallback/unwind without relying on native stack state.

## Coordinates and frames

X/Y/Z are generic coordinate functions. Meaning is supplied by a frame and relations among axes. A coordinate is semantically incomplete without its frame.

Reversible coordinate mappings remain distinct from semantic projections. Multi-edge frame traversal executes only through validated explicit mappings; semantic projections are not silently treated as reversible transforms.

## Tri-plane execution

```text
single 3D cast → frame-scoped coordinate
                     │
                     ├─ Plane 1: direction / form intent
                     ├─ Plane 2: admissible / authorized possibilities
                     └─ Plane 3: exception / recovery / fallback / recursion governance
```

Plane 1 proposes, Plane 2 admits, Plane 3 keeps fallback available. CPU recovery authority remains canonical.

Matrix cells may bind explicitly to normal and recovery Routes through generation-aware MatrixRouteBinding records. Route commitment uses a transaction ledger: PREPARE precedes COMMIT. Recovery routes require explicit matching RecoveryAuthorization before commit.

## Encoded Lexical Raster

ELR keeps immutable source bytes authoritative and derives aligned dense/sparse backing planes for classification, whitespace, escape, string, structural state, error state and depth. Dense raster discovery compacts into sparse structural/molecular representations.

Generic `FormFragment<T>` templates use local coordinates and explicit requirements. JSON-0 currently specializes them for byte/class literal fragments; the core remains independent of JSON.

## JSON-0

The CPU reference parser is iterative and emits:
- SourceSpan
- DataElement
- StructureNode
- SequenceElement
- Relation

Member structure is explicit: Object contains Member; Member has MemberKey and MemberValue relations; Member receives a complete key-through-value source span. Unicode `\\uXXXX` escapes validate surrogate-pair/scalar structure.

## Status boundary

CPU reference contracts are validated by tests. HIP, Win32 worker supervision, GPU recovery, and performance remain unvalidated until run on the target Windows 11 / RX 7700 XT system.


## v0.7 explicit execution topology and evidence

Recursive and recoverable execution is now represented by explicit runtime molecules/services rather than native stack state:

```text
ActivationGraph
  ├─ parent/child activation topology
  └─ transaction + generation context

ContinuationChain
  └─ explicit resumable return contracts

RecoveryDomain
  ├─ activations
  ├─ routes
  └─ backing objects sharing recovery fate

ExecutionEnvelope
  INTENT → PRECHECK → EFFECT → COMPLETE → COMMIT
                       └────────────→ FAULT (explicit diversion)

BreadcrumbRing + SemanticHeartbeat + FaultCapsule
  = forensic/reconstruction evidence, never execution authority
```

JSON-0 now binds derived parse products back to the immutable source through first-class Reference and Provenance records carrying the source generation.


## v0.9 integrity / recovery / mutation hardening

- `Digest256` + SHA-256 provide a tested integrity primitive.
- `IntegrityCommitCertificate` hashes its fixed identity/transaction/generation/validation fields, payload digest, and predecessor certificate digest.
- Integrity chaining is tamper-evident but does not prove signer identity or trusted timestamp; signatures/HMAC/TPM attestation remain separate future authority mechanisms.
- `RecoveryPlanCandidate` composes Checkpoint + Route + RecoveryDomain and validates generation, transaction, frame, activation membership, and route membership before reaching `AuthorizationRequired`.
- A separate matching `RecoveryAuthorization` is required to move the plan to `Authorized`; plan validation cannot self-authorize recovery.
- `resolve_cross_frame_cast` finds an explicit FrameGraph path, applies validated FrameMapping bindings, then performs the normal aligned tri-plane read at the mapped coordinate.
- JSON mutations use immutable-generation semantics: edits are bounds/overlap/generation checked, reconstruct a new source string, parse into a higher generation, and request full ELR rebuild. Existing JSON/ELR generations remain unchanged.
