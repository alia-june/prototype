# Package Manifest

**Package:** xOSG-0 operator/orchestrator kernel production release  
**Source candidate:** pre-production v0.8.0  
**Base evidence:** xOSG-0 Bare-Metal 0 v0.5.0 evidence line  
**State:** PRODUCTION — CONTROL KERNEL ACTIVE  
**Production gate:** PG-001 CLEARED for this release  
**Technical readiness:** PASS  
**Operator clearance:** CLEAR — explicit user instruction: “release production hold”  
**Decomposition:** NOT STARTED

## Promotion scope

This release promotes the **operator/orchestrator control kernel represented by this package**. It does not promote or deploy a successor system that has not yet been decomposed or designed.

Production activation preserves the existing non-escalation and theoretical-conversation constraints:

```text
THEORY != AUTHORITY
PROOF != PERMISSION
ORCHESTRATION != SOVEREIGNTY
STAGING != PRODUCTION
ROOT_GRANTED = INVALID_STATE
```

The user is the project **Operator** and owns binding design/research decisions. The assistant is the **Orchestrator** and instruments those decisions under Rule-0, Zero-Flight, Zero-Sentinel, phase control, and the production gate.

## Active Rule-0 chain

```text
SUB-ZERO → ABSOLUTE-ZERO → ZERO → ZERO-FLIGHT → ZERO-SENTINEL
```

- Sub-Zero: monotonic non-escalation; Operator/Orchestrator role separation.
- Absolute-Zero: descendants cannot weaken Sub-Zero.
- Zero: immutable admitted security baseline.
- Zero-Flight: live mutable in-flight rule plane bounded by Zero.
- Zero-Sentinel: final fail-closed guard.
- `ROOT_LIKE_RESTRICTED_ACCESS == CORE_ACCESS`; Core Access cannot exceed the Zero baseline.

## Validation at promotion

Shipped regression suites:

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

## Lineage

The package evolved through staged controls for the learning/diagnostics layer, production gate and memory model, source/security preferences, operational logic, meta-layer controls, Rule-0/Sub-Zero semantics, Zero-Flight/Zero-Sentinel separation, and Operator/Orchestrator role separation. Historical prompt and response logs preserve that progression.

## Current boundary

```text
CONTROL_KERNEL        = PRODUCTION_ACTIVE
PG-001                = CLEARED_FOR_THIS_RELEASE
ROOT_LOCKDOWN         = FALSE
DECOMPOSITION         = NOT_STARTED
SUCCESSOR_SYSTEM      = NOT_YET_DESIGNED
```

A material change to production semantics, authority boundaries, persistence, safety controls, external side effects, or release contents relocks PG-001 until the Operator clears the changed candidate.
