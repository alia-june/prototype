# xOSG-0 — ES-xOSG-7 to Seed

**Expert Overlay System Gestalt — Bare-Metal 0**

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Path](https://img.shields.io/badge/path-ES--xOSG--7%20%E2%86%92%20Seed-blue)
![Method](https://img.shields.io/badge/method-versioned%20growth-green)

xOSG-0 documents a developmental path from an earlier experimental system, **ES-xOSG-7**, through the xOSG-0 bare-metal line, ending in a distilled **Seed**.

The canonical spine is:

```text
ES-xOSG-7
    ↓
xOSG-0 bare-metal 0
    ↓
xOSG-0 v0.2 — actualized
    ↓
xOSG-0 v0.3 — deterministic testing + hardening
    ↓
xOSG-0 v0.4 — loose/fuzzy hardening
    ↓
Seed
```

That is the development story this repository is meant to show.

> **Prototype status:** this is a staging and research repository. No production authority is implied.

## Theoretical applications

The sequence is useful as a research model for:

- reducing a broad experimental AI/orchestration system into a smaller reusable kernel;
- learning architecture from successive failures rather than designing every control up front;
- explicit human/operator authority;
- bounded orchestration;
- provenance-aware state;
- fail-closed workflow design;
- deterministic offload;
- fuzz-driven hardening;
- extracting a seed only after the system has survived several generations of testing.

## 1. ES-xOSG-7 — genesis

ES-xOSG-7 is the predecessor and genesis condition.

It is the broad experimental source from which the xOSG-0 line is derived.

The point of the repository is **not** to call ES-xOSG-7 the seed. It is the larger antecedent system whose useful structure is progressively reduced and formalized.

## 2. xOSG-0 bare-metal 0

The first xOSG-0 stage strips the predecessor down into a compact explicit overlay.

Core structure:

```text
MACHINE DESCRIPTION
        ↓
TECHNICAL LOGIC
        ↓
OPERATING PROMPT
        ↓
NATURAL-LANGUAGE COMPATIBILITY
```

with the five working registers:

```text
NOTES
TODO
ERROR-LOG
AGENDA
ROADMAP
```

and the critical distinction:

```text
REQUEST != COMPLETION
```

This is the first **bare-metal reduction**, not the final Seed.

## 3. xOSG-0 v0.2 — actualized

v0.2 turns the bare-metal description into inspectable runtime behavior.

Added:

- persistent runtime state;
- persistent registers;
- runtime schema;
- CLI operations;
- explicit workflow transitions;
- provenance and change-control conventions.

The system is now executable enough to be challenged.

## 4. xOSG-0 v0.3 — deterministic testing and hardening

v0.3 subjects the actualized runtime to disciplined deterministic testing.

Growth here comes from finding structural weaknesses in:

- state transitions;
- persistence;
- verification;
- recovery;
- locking;
- corruption handling;
- boundary conditions.

The principle becomes:

```text
failure found
  → invariant stated
  → implementation hardened
  → regression added
```

## 5. xOSG-0 v0.4 — loose/fuzzy hardening

v0.4 deliberately stops assuming clean input.

The runtime is pressured with:

- malformed JSON;
- truncation;
- nullable structures;
- Unicode noise;
- ambiguous text;
- path-like and shell-like strings;
- repeated and randomized operation sequences;
- transaction and lock anomalies.

This stage asks a stronger question than "does it work?":

> **Does it fail in a bounded, inspectable way when the environment is wrong?**

The documented v0.4 fuzzy stage reached:

```text
Loose/fuzzy cases: 107
Passed:            107
Failures:            0
Crashes:             0
Timeouts:            0
```

## 6. Seed

Only **after v0.4** do we extract Seed.

Seed is not a historical version number and not a copy of the whole system.

It is the smallest coherent package that survives the entire path:

```text
ES-xOSG-7
  → bare-metal reduction
  → actualization
  → deterministic hardening
  → fuzzy hardening
  → SEED
```

A component belongs in Seed only if it is:

- necessary;
- explicit;
- bounded;
- testable;
- provenance-traceable;
- non-redundant;
- supported by the developmental evidence.

Conceptually:

```text
SEED =
    surviving invariants
  + minimum mechanisms
  + explicit boundaries
  + regression obligations
```

## Supporting development

The uploaded operator kernel, operator/orchestrator kernel, learning layer, deterministic control kernel, and goal-scaffolding packages are **supporting development artifacts**.

They help explain how particular controls emerged and may feed the v0.3/v0.4 line, but they do not replace the canonical version spine.

The canonical story remains:

```text
ES-xOSG-7
 -> xOSG-0 bare-metal
 -> v0.2
 -> v0.3
 -> v0.4
 -> Seed
```

## Repository map

```text
syn-xOSG-0/
├── README.md
├── growth/
│   ├── README.md
│   └── spine/
│       ├── 00-es-xosg-7/
│       ├── 01-xosg-0-baremetal/
│       ├── 02-xosg-0-v0.2/
│       ├── 03-xosg-0-v0.3/
│       ├── 04-xosg-0-v0.4/
│       └── 05-seed/
├── docs/
├── history/
└── supporting/
```

See **[growth/README.md](growth/README.md)** for the canonical developmental spine.
