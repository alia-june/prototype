# GFX Form Engine

**GFX Form Engine is a C++20 research scaffold for representing structured data, execution, and recovery in frame-scoped coordinate spaces.** It explores how one 3D cast can locate a candidate, then use three aligned reads to describe intent, admissible possibilities, and recovery options. JSON-0 and the Encoded Lexical Raster (ELR) give the architecture a concrete first workload.

## What could it be used for?

| Theoretical use | What the architecture lets us explore |
| --- | --- |
| **Source-preserving data inspection** | Navigate derived structure while keeping the original bytes, spans, and generation available. An inspector could follow a Relation from an array to its elements, then trace a selected element back to the exact source text that produced it. |
| **Spatial search and signaling** | Let a voxel cast a configurable ray to discover a nearby or distant target without walking the neural graph. A cast could find a candidate, propose a signal, or point to a possible execution target. A spatial hit does not create a neural connection or grant permission to execute. |
| **Composable neural engines** | Let voxels host small neural engines with a limited number of declared inputs and outputs. Engines could use shared parameters, specialized parameters, or both. A composition could report its current construction so that a cast can be directed against the right generation. A voxel's *sensorium* could observe surrounding activity through passive observation and active probing, including activity from engines to which it has no neural connection. |
| **Inspectable execution and recovery** | Track what started an operation, what work remains suspended, and which checkpoints or recovery routes are available. Plane 3 could govern recursion recovery through progress, resources, and state validity without a universal depth cap. Recovery actions would still require CPU authority. |

These are research directions. The current scaffold exercises parts of the data, coordinate, execution, and recovery models on the CPU. It does not yet implement a voxel neural network or a sensorium. Carbon-inspired and buckyball-like voxel assemblies remain topology research; their geometry does not set engine port counts or determine connectivity.

## How the engine is organized

Primitive forms define concrete schemas for Atomics. The initial Atomic families are **Identity**, **Code**, **Value**, and **Mask**. Binding associates roles and values; Relation describes links; Reference gives a target an explicit identity and context; Validation records checks; Provenance records origin and derivation. Larger structures, including voxels, are compositions of these forms. Reference and Recursion are first class. Activation, Continuation, and Progress make execution context explicit without relying on native call-stack depth. Machine bitcodes and packed layouts remain unfrozen where the distinctions are still being tested.

XYZ meanings are defined by the active **frame**. An explicit mapping can change how a location is addressed across frames. A change to network connections or parameter bindings would be a separate, declared change to the composition.

```text
one 3D cast → one frame-scoped location
                  ├─ Plane 1: direction or form intent
                  ├─ Plane 2: admissible possibilities
                  └─ Plane 3: fallback, recovery, and recursion governance
```

The three planes are read at the same location and generation. Plane 3 can identify recovery candidates; CPU authority determines whether a candidate can be carried out. A configured ray, the signal it may deliver, and any resulting activation have distinct roles.

## Start with JSON-0

JSON-0 starts with immutable source text and builds an **Encoded Lexical Raster**: byte classification, escape and string state, structural positions, and nesting depth. The iterative CPU parser derives spans, nodes, Relations, and sequencing with source lineage. The document retains the original text so it can return the same whitespace and escapes. A generation-bound edit creates and reparses new source while preserving the prior generation and identifying the need to rebuild dependent ELR data.

The v0.9 scaffold also includes cross-frame resolution followed by aligned plane reads, recovery-plan validation and separate authorization, and SHA-256-linked commit certificates. The digest chain records integrity evidence; signer authenticity and durable crash recovery remain separate work.

## Build the CPU scaffold

From the [v0.9 scaffold directory](scaffolds/v0.9/), use **CMake 3.20 or later** and a **C++20 compiler**. The CPU path does not require HIP.

```sh
cmake -S . -B build
cmake --build build --config Debug
ctest --test-dir build -C Debug --output-on-failure
```

The [v0.9 build report](scaffolds/v0.9/docs/BUILD_REPORT_v0.9.md) records **38/38 CPU tests passing** in the scaffold build, including an iterative parse of 5,000 nested arrays. That case exercises the parser's explicit stack; it does not set a project-wide depth limit.

The intended hardware target is **Windows 11 x86-64 with an AMD Radeon RX 7700 XT and the AMD HIP SDK**. Target GPU execution, Windows worker supervision, durable commit behavior, and performance are outside the reported v0.9 validation. See the [Decision Ledger](scaffolds/v0.9/logs/DECISION_LEDGER.md) and [Change Log](scaffolds/v0.9/logs/CHANGELOG.md) for the scaffold's design record.

## Scaffold and reference archive

- [Architecture](ARCHITECTURE.md) and [original reference bundle](references/README.md).
- [v0.1 design scaffold](scaffolds/v0.1/SCAFFOLD.md); C++ source snapshots: [v0.2](scaffolds/v0.2/README.md), [v0.3](scaffolds/v0.3/README.md), [v0.4](scaffolds/v0.4/README.md), [v0.5](scaffolds/v0.5/README.md), [v0.6](scaffolds/v0.6/README.md), [v0.7](scaffolds/v0.7/README.md), [v0.8](scaffolds/v0.8/README.md), [v0.9](scaffolds/v0.9/README.md).
- [Snapshot notes](SNAPSHOTS.md) and [staged-file checksums](STAGED_SHA256SUMS.txt).
