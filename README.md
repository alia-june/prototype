<div align="center">

# prototype

### Human-led systems for bounded orchestration, reference-native documents, and deterministic computation

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Visibility](https://img.shields.io/badge/repository-public-2da44e)
![Method](https://img.shields.io/badge/method-evidence--first-2f81f7)
![Authority](https://img.shields.io/badge/authority-human--led-6f42c1)
![Failure](https://img.shields.io/badge/failure-fail--closed-b23c17)

**Public research prototypes for systems that keep semantics, execution, authority, provenance, and verification visibly separate.**

<br>

![AI orchestration](https://img.shields.io/badge/AI-orchestration-informational)
![Deterministic systems](https://img.shields.io/badge/deterministic-systems-informational)
![Document transformation](https://img.shields.io/badge/document-transformation-informational)
![Numerical computing](https://img.shields.io/badge/numerical-computing-informational)
![Provenance](https://img.shields.io/badge/provenance-aware-informational)
![Fuzz testing](https://img.shields.io/badge/fuzz-testing-informational)

</div>

---

## Overview

This repository contains four related prototype families exploring a common question:

> **How can complex AI-assisted systems remain inspectable when execution, authority, verification, provenance, and failure are distributed across multiple layers?**

| Project | Core question | Current direction |
| --- | --- | --- |
| **[xOSG-0](syn-xOSG-0/README.md)** | How can a human-directed AI/software system grow through explicit authority, state, testing, and reduction? | ES-xOSG-7 → bare-metal → v0.2 → v0.3 → v0.4 → Seed |
| **[Etabit Schema](etabit-schema/README.md)** | How can multi-drive referential construction and distributed authority be described without granting execution authority? | Draft JSON Schema, source/reference examples, and explicit unresolved contracts |
| **[Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md)** | How can documents remain reference-native, non-destructive, inspectable, and transformable across formats? | Markdown-first, JSON-governed document transformation with a retained CPU compatibility service |
| **[sf-AmorphDataDrive](sf-amorph-data-drive/README.md)** | How can raw enumerated values remain free of identity and metadata while external relations and compositions build coherent structures? | Locked v0.3 with open identity, bitmap, topology, and recursion contracts |
| **[MATH.SC-0](xosg-0-math-sc0/README.md)** | How can AI-operated numerical work be delegated to deterministic computation instead of language-model inference? | Exact, interval, Python, native C/C++, and heterogeneous numerical execution with independent verification |

These are separate research systems, not one finished product. Each keeps its own contracts, evidence, compatibility boundaries, validation status, integration gates, and release decisions.

> **Make the boundary visible. Keep evidence attached. Do not turn uncertainty into authority.**

---

## System landscape

```text
                         HUMAN / OPERATOR
                               │
                      explicit decision authority
                               │
                ┌──────────────┴──────────────┐
                │                             │
             xOSG-0                     bounded services
      orchestration / control          /                \
                │                    /                    \
                │        Syn-Etabit Transformer        MATH.SC-0
                │        document semantics            computation
                │              │                           │
                │       immutable states            deterministic backends
                │       transformations             exact / interval / native
                │       receipts + recovery         verification + evidence
                │              │                           │
                └──────── provenance / gates / explicit failure ────────┘
```

This is a conceptual map, not a dependency graph.

---

# Project constellation

## xOSG-0 — developmental orchestration spine

**[Open project →](syn-xOSG-0/README.md)** · **[Growth spine →](syn-xOSG-0/growth/README.md)** · **[Source ledger →](syn-xOSG-0/docs/SOURCE_LEDGER.md)**

xOSG-0 is the repository's governance and orchestration research line. It records how a broad experimental system is reduced, actualized, pressured, hardened, and finally distilled toward a smaller Seed.

```text
ES-xOSG-7
    ↓
xOSG-0 bare-metal 0
    ↓
xOSG-0 v0.2 — actualized runtime
    ↓
xOSG-0 v0.3 — deterministic testing + hardening
    ↓
xOSG-0 v0.4 — loose/fuzzy hardening
    ↓
Seed
```

Research themes include layered human/operator authority, explicit workflow state, deterministic offload, provenance-aware transitions, fail-closed behavior, fuzzy/adversarial pressure, and extracting a minimum justified kernel only after developmental evidence exists.

The documented v0.4 fuzzy stage records **107 / 107 bounded cases passing with no crashes or timeouts**. The source ledger also preserves historical uncertainty: reconstructed evidence is not silently relabeled as recovered original source.

---

## sf-AmorphDataDrive — strict raw-substrate architecture

**[Open project →](sf-amorph-data-drive/README.md)** · **[Locked v0.3 →](sf-amorph-data-drive/specifications/sf_edabit_amorph_data_drive_locked_spec_v0_3.md)** · **[Relation to Etabit →](sf-amorph-data-drive/docs/ETABIT_RELATION.md)**

sf-AmorphDataDrive separates raw existence, relation/interpretation, and composition/coherence. Locked v0.3 prohibits identity and metadata on raw D0. Current successor direction introduces member sf-UUID, touple-to-gestalt/gesple construction, and recursive ID/data/metadata integration while leaving identity, topology, bitmap, width, and recursion contracts open.

It is related to Etabit as a possible strict substrate profile; no integration is admitted.

---

## Syn-Etabit Transformer — Textual

**[Open project →](syn-etabit-transformer-textual/README.md)** · **[Compatibility service →](syn-etabit-transformer-textual/service/README.md)** · **[Integration boundaries →](syn-etabit-transformer-textual/INTEGRATIONS.md)**

Syn-Etabit explores a document model in which text, structure, metadata, transformations, assets, and emitted artifacts retain separate identities instead of collapsing early into one opaque file.

```text
Markdown content
      +
JSON-governed document plan
      ↓
reference-native state
      ↓
ordered transformations
      ↓
resolved immutable package
      ↓
EJECT → TRANSFORM → EJECTION
      ↓
derived artifact + receipt
```

The retained CPU compatibility implementation includes immutable semantic snapshots, typed transformations, logical output streams, an explainable reducer, SQLite receipts/recovery, rendering, Markdown/DOCX adapters, and rigid/fuzzy/torture harnesses.

Open findings remain visible: rigid and bounded torture checks pass, while the retained 500-case fuzzy run exposes **three character/conversion finding groups**.

External capabilities such as WordNet, external conversion, GPU execution, and agentic control remain explicit integration boundaries rather than automatic dependencies.

---

## xOSG-0 MATH.SC-0 — Straight Computation Core

**[Open project →](xosg-0-math-sc0/README.md)** · **[Build / test evidence →](xosg-0-math-sc0/BUILD_TEST_REPORT.txt)** · **[Current wall →](xosg-0-math-sc0/docs/hardening_and_walls.md)**

MATH.SC-0 is the deterministic numerical substrate. Its purpose is to keep mathematical execution out of the language model whenever a deterministic backend can perform and verify the work.

```text
JavaScript
contract + authority plane
        ↓
Python
numerical semantics + verification
        ↓
C / C++
native deterministic kernels
        ↓
independent checks + numerical evidence
        ↓
web, only where admitted
        ↓
LLM, strict last resort
```

Current v0.8.0 work includes exact rational arithmetic, high precision, exact rational intervals, directed-rounding transcendental intervals, determinant/solve/inverse, native LU kernels, residual and conditioning diagnostics, replay fingerprints, resource ceilings, and differential/metamorphic/containment tests.

| Evidence | Result |
| --- | ---: |
| Python tests | **58 / 58 PASS** |
| JavaScript / integration tests | **23 / 23 PASS** |
| Native self-test | **PASS** |
| AddressSanitizer / UBSan | **PASS** |
| Seeded interval containment | **PASS** |
| Native LU differential testing | **PASS** |
| Exact metamorphic identities | **PASS** |

The current higher-assurance wall is explicit: independent compiled MPFR verification and real GPU/open-compute certification require development headers and hardware/runtime support outside the reference host.

---

# Shared design language

| Principle | Meaning here |
| --- | --- |
| **Request ≠ completion** | Asking for an action is not evidence that it occurred. |
| **Generation ≠ verification** | The component that produced a result does not automatically certify it. |
| **Authority is explicit** | Human, policy, runtime, verifier, and external-service roles remain distinguishable. |
| **Fail closed** | Invalid, ambiguous, unsupported, or excessive requests should remain visible failures. |
| **Provenance survives transformation** | Successor states, conversions, and derived artifacts retain traceable origins. |
| **External integrations begin closed** | A documented integration is not the same thing as an activated integration. |
| **Reference behavior precedes acceleration** | Faster implementations must remain comparable to the semantic reference. |
| **Evidence scopes claims** | A passing test proves the stated test, not general production readiness. |
| **History is not rewritten** | Working names, prior interfaces, findings, and reconstructed evidence remain distinguishable from current design. |

---

## Theoretical application space

Taken together, the work explores:

- human-led AI orchestration with bounded machine initiative;
- inspectable multi-stage workflows;
- deterministic services underneath language-model interfaces;
- AI-native document genesis and non-destructive revision;
- provenance-aware scientific and engineering computation;
- capability-aware execution across heterogeneous machines;
- explicit integration and production gates;
- adversarial and fuzzy testing as architecture discovery;
- reusable kernels distilled from larger experimental systems.

The emphasis is not on claiming these problems are solved. The emphasis is on making the path from **idea → mechanism → pressure → evidence → boundary** inspectable.

---

## Repository map

```text
prototype/
│
├── syn-xOSG-0/
│   ├── growth/                 canonical developmental spine
│   ├── docs/                   source and boundary records
│   ├── history/                retained development evidence
│   └── supporting/             supporting kernels and mechanisms
│
├── etabit-schema/              standalone Etabit architectural schema research
│   ├── schema/                draft research descriptor schema
│   ├── examples/              illustrative four-symbol source
│   └── docs/                  decisions and open contracts
│
├── sf-amorph-data-drive/       strict raw-substrate architecture
│   ├── specifications/         locked v0.2/v0.3 baselines
│   ├── docs/                   direction and boundaries
│   └── evidence/               review summaries
│
├── syn-etabit-transformer-textual/
│   ├── service/                retained CPU compatibility implementation
│   ├── docs/                   contracts, validation, findings, integrations
│   └── ...                     transformation and research artifacts
│
└── xosg-0-math-sc0/
    ├── js/                     JavaScript control plane + frozen web UI
    ├── src/                    Python numerical and verification plane
    ├── native/                 C/C++ kernels
    ├── protocol/               operation and result contracts
    ├── tests/                  numerical and hardening suites
    └── docs/                   architecture, evidence, walls
```

---

## Start here

1. **[xOSG-0](syn-xOSG-0/README.md)** — developmental and authority model.
2. **[Etabit Schema](etabit-schema/README.md)** — multi-drive construction and distributed-authority schema research.
3. **[Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md)** — reference-native document model.
4. **[MATH.SC-0](xosg-0-math-sc0/README.md)** — deterministic computation architecture.
4. Read each project's validation, source-boundary, and integration documents before treating test results as broader acceptance.

- **[sf-AmorphDataDrive](sf-amorph-data-drive/README.md)** — strict raw substrate and open successor contracts.

---

## Public repository boundary

This is a **public prototype and research repository**.

Public visibility does not change the status of the work. The presence of code, passing tests, a historical release label, or a documented integration does **not** imply production deployment, autonomous authority, external activation, or general certification.

Machine-local environments, caches, mutable runtime stores, installed browser distributions, downloaded third-party payloads, and other host-specific material are intentionally excluded where they would blur the boundary between source and environment.

Each project retains its own decisions, contracts, compatibility boundaries, evidence, validation status, integration gates, and production gate.

---

<div align="center">

---

**Prototype systems should make their limits easier to inspect, not easier to forget.**

</div>
