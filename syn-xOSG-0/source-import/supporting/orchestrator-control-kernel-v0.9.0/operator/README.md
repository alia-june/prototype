# Operator Kernel, Learning & Diagnostics Layer

**Status:** PRODUCTION-ACTIVE operator/orchestrator control kernel  
**Base:** xOSG-0 Bare-Metal 0 v0.5.0  
**Purpose:** Provide the production-active control discipline used before and during Operator-directed successor-system construction.

This directory is deliberately separate from the v0.5.0 normative source. It does not claim to modify the underlying model, hidden instructions, privileges, or external capabilities.

## Kernel and control

- `KERNEL_UPGRADE.md`
- `gates/PHASE_CONTROL.md`
- `gates/PRODUCTION_GATE.md`

## Operator / Orchestrator boundary

```text
OPERATOR     = binding design/research decision agency
ORCHESTRATOR = instrumentation, coordination, validation, and reporting
```

## Active Rule-0 chain

```text
SUB-ZERO → ABSOLUTE-ZERO → ZERO → ZERO-FLIGHT → ZERO-SENTINEL
```

## Validation at promotion

```text
Operational regression           18/18 PASS
Meta-layer regression            23/23 PASS
Rule-0/Sub-Zero regression       38/38 PASS
Zero-Flight runtime               7/7 PASS
Operator/Orchestrator boundary   18/18 PASS
-------------------------------------------
Total                           104/104 PASS
```

Additional promotion checks: production-readiness regression 13/13 PASS; adversarial reference-model regression 28/28 PASS; Python compilation PASS; pre-promotion internal SHA-256 manifest verification PASS. Total release checks: **145/145 PASS**.

## Current boundary

```text
CONTROL_KERNEL        = PRODUCTION_ACTIVE
PG-001                = CLEARED_FOR_THIS_RELEASE
ROOT_LOCKDOWN         = FALSE
DECOMPOSITION         = NOT_STARTED
SUCCESSOR_SYSTEM      = NOT_YET_DESIGNED
```

A material change to production semantics, authority boundaries, persistence, safety controls, external side effects, or release contents relocks PG-001 until the Operator clears the changed candidate.
