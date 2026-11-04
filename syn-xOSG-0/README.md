# xOSG-0 — Growing a Seed

**Expert Overlay System Gestalt — Bare-Metal 0**

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Method](https://img.shields.io/badge/method-seed%20growth-blue)
![Principle](https://img.shields.io/badge/principle-test%20before%20promotion-green)

xOSG-0 is a research project about a specific systems question:

> **How can a very small, coherent control seed be grown into a larger orchestration system without losing its original invariants?**

The repository is therefore organized to show **growth**, not merely a sequence of releases.

A seed begins small. It is exposed to use, failure, ambiguity, and pressure. New structure is added only when the seed cannot safely express or survive something it now needs to do.

> **Prototype status:** this repository is a staging and research environment. It does not imply deployment authority, hidden agents, privilege escalation, or modification of an underlying model.

## Theoretical applications

The seed-growth method can be studied as a model for:

- layered authority and governance systems;
- human-directed AI orchestration;
- bounded autonomy;
- capability and permission separation;
- provenance-aware computation;
- fail-closed workflow design;
- deterministic offload from probabilistic systems;
- adversarial and fuzzy development;
- heterogeneous-system composition;
- multi-instance coordination;
- control-plane separation;
- machine-readable capability envelopes;
- learning systems that accumulate rules without silently replacing their foundation.

The central research idea is not that a finished architecture should be designed all at once. It is that a sufficiently coherent seed can **grow structure in response to evidence**.

## The seed

The early xOSG-0 seed contained only a few essential ideas:

```text
MACHINE DESCRIPTION
        ↓
TECHNICAL LOGIC
        ↓
OPERATING PROMPT
        ↓
NATURAL-LANGUAGE COMPATIBILITY
```

with five persistent conceptual registers:

```text
NOTES
TODO
ERROR-LOG
AGENDA
ROADMAP
```

and one critical execution distinction:

```text
REQUEST != COMPLETION
```

That is enough to begin.

A useful seed should be:

- **small** enough to understand;
- **explicit** enough to inspect;
- **coherent** enough to constrain later additions;
- **testable** enough to be challenged;
- **incomplete** enough that real use can reveal what must grow next.

## How the seed grows

xOSG-0 uses an evidence-driven growth loop:

```text
SEED
  ↓
ACTUALIZE
  ↓
USE
  ↓
BREAK / FUZZ / CONTRADICT
  ↓
OBSERVE FAILURE
  ↓
EXTRACT LESSON
  ↓
FORM INVARIANT
  ↓
ADD MINIMUM STRUCTURE
  ↓
REGRESSION TEST
  ↓
PROMOTE ONLY WHEN JUSTIFIED
  ↓
NEW SEED SURFACE
```

The output of one growth cycle becomes the input surface for the next.

### Growth rule

```text
NEW_STRUCTURE requires:
    observed_need
    + explicit_invariant
    + failure_model
    + implementation_or_procedure
    + negative_test
    + regression_evidence
```

A feature is not added merely because it is interesting.

## Growth rings in this repository

The uploaded project artifacts show several distinct growth rings.

### 0 — Bare seed

**Problem:** create a minimal orchestration overlay that is readable by both machine and human.

**Added:** machine description, technical logic, operating prompt, compatibility layer, registers, verification concept.

**Evidence:** original bare-metal artifact.

### 1 — Actualization

**Pressure:** the seed was mostly declarative; state existed conceptually but not operationally.

**Added:** persistent runtime state, register persistence, CLI behavior, runtime schema, explicit requested-vs-completed action semantics.

**Evidence:** bare-metal actualized artifact.

### 2 — Adversarial pressure

**Pressure:** normal-path tests were insufficient.

**Method:** loose and fuzzy input, malformed JSON, null structures, Unicode noise, repeated operations, corruption.

**Observed failures:** nullable verification crashes and raw JSON parser failures.

**Growth:** defensive load boundaries, controlled invalidity, regression targets.

**Evidence:** fuzzy-suite artifact and reports.

### 3 — Learning layer

**Pressure:** individual fixes were accumulating faster than architectural understanding.

**Added:** a pre-decomposition learning stack:

```text
ERROR LOGS
  ↓
LESSONS
  ↓
PATTERNS / ANTIPATTERNS
  ↓
LOGIC
  ↓
META-LOGIC
  ↓
ANALYSIS
  ↓
META-ANALYSIS
```

The important step here is that failures stop being isolated bugs and become material for disciplined learning.

**Evidence:** operator learning-layer package.

### 4 — Operator kernel

**Pressure:** the system needed a disciplined way to distinguish observation, inference, proposal, execution, and promotion.

**Added:**

- epistemic state;
- action-state transitions;
- specification / implementation / test / evidence separation;
- mutation records;
- failure-learning discipline;
- explicit phase and production gates.

**Evidence:** operator-kernel preproduction package.

### 5 — Operator / Orchestrator separation

**Pressure:** orchestration authority could otherwise blur into decision authority.

**Added:** explicit role separation:

```text
OPERATOR     = binding decision agency
ORCHESTRATOR = instrumentation and coordination
```

along with Rule-0 security layers and production-gate semantics.

**Evidence:** operator/orchestrator kernel production release.

### 6 — Deterministic offload

**Pressure:** too much validation and attestation still required semantic model contact.

**Added:** deterministic-first orchestration, Gestalt Hypervisor, minimum-sufficient tasks, hashing/attestation, task graph, minimized evidence return.

```text
OPERATOR DECISION
 -> ORCHESTRATOR INTENT
 -> DETERMINISTIC TASK
 -> MINIMIZED EVIDENCE
 -> SYNTHESIS
 -> SENTINEL
 -> REPORT
```

**Evidence:** orchestrator control-kernel v0.9.0.

### 7 — Goal scaffolding

**Pressure:** compact symbolic goals needed context without allowing symbols to acquire accidental authority.

**Added:** deterministic goal scaffolding, descriptor registries, opaque-token semantics, exact payload preservation.

Critical invariants include:

```text
TOKEN_SPELLING != TOKEN_SEMANTICS
CORE_ACCESS != PRIVILEGE
WRAPPING != EXECUTION
DESCRIPTOR != PERMISSION
PAYLOAD_AFTER == PAYLOAD_BEFORE
```

**Evidence:** goal-scaffolding v0.10.0.

## What this demonstrates

The system did not grow by starting with a giant architecture diagram.

It grew by repeatedly asking:

1. **What can the seed already express?**
2. **Where does it fail under real pressure?**
3. **What is the smallest missing primitive?**
4. **Can that primitive be stated as an invariant?**
5. **Can we test its absence and its presence?**
6. **Does the new structure preserve the seed beneath it?**

That is the method this repository is intended to expose.

## Seed preservation

Growth is not replacement.

A later layer may add structure, but it should not silently erase the seed's earlier constraints.

Conceptually:

```text
SEED_0
  ⊂ SEED_1
  ⊂ SEED_2
  ⊂ ...
```

where each new ring should preserve justified invariants from the prior ring unless an explicit, evidenced redesign retires them.

This is **developmental inheritance**, not blind backward compatibility.

## Repository map

```text
syn-xOSG-0/
├── README.md
├── growth/
│   ├── README.md
│   ├── 00-seed/
│   ├── 01-actualization/
│   ├── 02-adversarial-pressure/
│   ├── 03-learning-layer/
│   ├── 04-operator-kernel/
│   ├── 05-operator-orchestrator/
│   ├── 06-deterministic-offload/
│   └── 07-goal-scaffolding/
├── docs/
│   └── PROVENANCE.md
└── history/
    └── ...
```

**growth/** explains how one structure caused the next.

**history/** preserves recoverable historical source and evidence.

The two are deliberately different.

## Start with the seed

Do not begin by copying the final system.

Begin with the smallest coherent seed, then reproduce the pressures that caused it to grow.

See **[growth/README.md](growth/README.md)** for the step-by-step development path.
