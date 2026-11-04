<div align="center">

# prototype

### Human-led systems for bounded orchestration, document transformation, and deterministic computation

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Method](https://img.shields.io/badge/method-evidence--first-2f81f7)
![Authority](https://img.shields.io/badge/authority-human--led-6f42c1)
![Failure](https://img.shields.io/badge/failure-fail--closed-b23c17)
![Repository](https://img.shields.io/badge/repository-private-lightgrey)

**A private research container for systems that keep semantics, execution, authority, provenance, and verification visibly separate.**

</div>

---

## What this repository is

This repository contains three related prototype families:

| Project | Core question | Current direction |
| --- | --- | --- |
| **[xOSG-0](syn-xOSG-0/README.md)** | How can a human-directed AI/software system grow through explicit authority, state, testing, and reduction? | ES-xOSG-7 → bare-metal → v0.2 → v0.3 → v0.4 → Seed |
| **[Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md)** | How can documents remain reference-native, non-destructive, inspectable, and transformable across formats? | Markdown-first, JSON-governed document transformation with a retained CPU compatibility service |
| **[MATH.SC-0](xosg-0-math-sc0/README.md)** | How can AI-operated numerical work be delegated to deterministic computation instead of language-model inference? | Exact, interval, Python, native C/C++, and heterogeneous numerical execution with independent verification |

They are not presented as one finished product. They are separate research systems with a shared design language:

> **Make the boundary visible. Keep evidence attached. Do not turn uncertainty into authority.**

---

## The system landscape

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

This is a conceptual map, not a dependency graph. Each project keeps its own contracts, evidence, compatibility boundaries, and release status.

---

# Project constellation

## xOSG-0 — developmental orchestration spine

**[Open project →](syn-xOSG-0/README.md)**  
**[Canonical growth spine →](syn-xOSG-0/growth/README.md)**  
**[Source ledger →](syn-xOSG-0/docs/SOURCE_LEDGER.md)**

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

The line develops ideas including:

- layered human/operator authority;
- explicit workflow state and persistent registers;
- bounded orchestration rather than implicit autonomy;
- deterministic offload from probabilistic reasoning;
- provenance-aware state transitions;
- fail-closed behavior;
- fuzzy and adversarial pressure as a source of design knowledge;
- extraction of a minimum justified kernel only after developmental evidence exists.

The documented v0.4 fuzzy stage records **107 / 107 bounded cases passing with no crashes or timeouts**. The source ledger also keeps the historical boundary explicit: ES-xOSG-7 source has not yet been recovered, and reconstructed v0.3/v0.4 evidence is not silently relabeled as original source.

Supporting development includes the operator kernel, operator/orchestrator kernel, learning layer, deterministic control kernel, and goal-scaffolding work. Those explain mechanisms inside the lineage without replacing the canonical version spine.

---

## Syn-Etabit Transformer — Textual

**[Open project →](syn-etabit-transformer-textual/README.md)**  
**[Compatibility service →](syn-etabit-transformer-textual/service/README.md)**  
**[Integration boundaries →](syn-etabit-transformer-textual/INTEGRATIONS.md)**

Syn-Etabit explores a document model in which text, structure, metadata, transformations, assets, and emitted artifacts retain separate identities instead of collapsing early into one opaque file.

Its forward model is:

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

The retained compatibility implementation currently provides:

- immutable semantic snapshots;
- typed transformations;
- logical output streams;
- an explainable reducer;
- SQLite-backed receipts and recovery;
- rendering;
- Markdown and DOCX adapters;
- controlled image/table/list support;
- rigid, fuzzy, and torture harnesses.

The project deliberately preserves open findings. Rigid and bounded torture checks pass, while the retained 500-case fuzzy run still exposes **three character/conversion finding groups**. Those findings remain visible rather than being normalized away to make the project appear green.

External capabilities remain behind explicit integration gates. WordNet, external conversion, GPU execution, and agentic control are documented as replaceable boundaries rather than automatically activated dependencies.

---

## xOSG-0 MATH.SC-0 — Straight Computation Core

**[Open project →](xosg-0-math-sc0/README.md)**  
**[Build / test evidence →](xosg-0-math-sc0/BUILD_TEST_REPORT.txt)**  
**[Hardening and current wall →](xosg-0-math-sc0/docs/hardening_and_walls.md)**

MATH.SC-0 is the deterministic numerical substrate. Its purpose is to keep mathematical execution out of the language model whenever a deterministic backend can do the work.

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

Current v0.8.0 work includes:

- exact rational arithmetic;
- high-precision computation;
- exact rational interval arithmetic;
- directed-rounding transcendental intervals;
- determinant, solve, and inverse;
- native C/C++ LU kernels;
- residual and conditioning diagnostics;
- replay fingerprints;
- resource ceilings;
- seeded differential, containment, and metamorphic tests;
- terminal failure for known contracted operations rather than fallback substitution.

Current recorded verification:

| Evidence | Result |
| --- | ---: |
| Python tests | **58 / 58 PASS** |
| JavaScript / integration tests | **23 / 23 PASS** |
| Native self-test | **PASS** |
| AddressSanitizer / UBSan | **PASS** |
| Seeded interval containment | **PASS** |
| Native LU differential testing | **PASS** |
| Exact metamorphic identities | **PASS** |

The current wall is environmental, not hidden: independent compiled MPFR verification and real GPU/open-compute certification require development headers and hardware/runtime support not present on the reference host.

Abstract logic, sets, relations, predicates, and abstract objects remain deliberately outside this numerical module.

---

# Shared design language

Across the repository, the projects repeatedly converge on the same engineering rules.

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

Taken together, the work explores a broader class of systems:

- human-led AI orchestration with bounded machine initiative;
- inspectable multi-stage workflows;
- deterministic services underneath language-model interfaces;
- AI-native document genesis and continuous non-destructive revision;
- provenance-aware scientific and engineering computation;
- replaceable integration layers;
- capability-aware execution across heterogeneous machines;
- explicit production gates and release authority;
- adversarial and fuzzy testing as part of architecture discovery;
- reusable kernels distilled from larger experimental systems.

The emphasis is not on pretending those problems are already solved. The emphasis is on making the path from **idea → mechanism → pressure → evidence → boundary** inspectable.

---

# Repository map

```text
prototype/
│
├── syn-xOSG-0/
│   ├── growth/                 canonical developmental spine
│   ├── docs/                   source and boundary records
│   ├── history/                retained development evidence
│   └── supporting/             supporting kernels and mechanisms
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

If you are approaching the repository for the first time:

1. Read **[xOSG-0](syn-xOSG-0/README.md)** for the developmental and authority model.
2. Read **[Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md)** for the reference-native document model.
3. Read **[MATH.SC-0](xosg-0-math-sc0/README.md)** for the deterministic computation architecture.
4. Follow each project's validation, source-boundary, and integration documents before interpreting test results as broader acceptance.

---

## Repository boundary

This is a **private prototype and research repository**.

The presence of code, passing tests, a historical release label, or a documented integration does **not** imply production deployment, autonomous authority, external activation, or general certification.

Machine-local environments, caches, mutable runtime stores, installed browser distributions, downloaded third-party payloads, and other host-specific material are intentionally excluded where they would blur the boundary between source and environment.

Each project retains its own:

```text
decisions
contracts
compatibility boundaries
evidence
validation status
integration gates
production gate
```

<div align="center">

---

**Prototype systems should make their limits easier to inspect, not easier to forget.**

</div>
