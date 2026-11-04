# Current Memory — Volatile Project State

**Type:** Working/session memory snapshot  
**Authority:** Descriptive, not independently normative  
**Persistence expectation:** May be replaced as the active state changes.

## Current objective
Operate the released control kernel and await Operator direction for successor-system decomposition.

## Current state

- Base evidence package: xOSG-0 Bare-Metal 0 v0.5.0.
- v0.5.0 is treated as experimental evidence, not the successor blueprint.
- Operator kernel controls are defined.
- Learning/diagnostics documents exist.
- Production Gate `PG-001` is cleared for the current control-kernel release.
- Ground-zero decomposition has **not** started.
- Production of the control kernel **has been authorized** by the Operator; the successor system is not yet designed.

## Active instructions from the user

1. Do not jump ahead of the requested phase.
2. The user must explicitly clear the production gate.
3. Maintain error logs, lessons, patterns, anti-patterns, logic, meta-logic, analysis, and meta-analysis.
4. Add explicit memory layers, prompt history, and response logging.

## Current next boundary
Remain at the post-release phase boundary until the Operator explicitly directs successor-system decomposition or another major phase.

## What this file is not
This is not hidden chain-of-thought, model weights, or a dump of internal system instructions. It is a project-visible operational memory snapshot.

## Current source/security preference

SPS-001 defines source preference levels 0–4 and is active in the production control kernel. Decomposition is still not started.

## Enforcement distinction

`SPS-001` is active as production control-kernel security discipline for prompt analysis, source admission, staging, and response construction. It does not by itself define the not-yet-designed successor architecture.

## Current control extension — operational logic layer

```text
OPERATIONAL_AXIOMS          = PRODUCTION_ACTIVE
OPERATIONAL_PROPOSITIONS    = PRODUCTION_ACTIVE
OPERATIONAL_LOGICS          = PRODUCTION_ACTIVE
OPERATIONAL_LOGIC_STACKS    = PRODUCTION_ACTIVE
OPERATIONAL_REGRESSION      = PRODUCTION_ACTIVE
OP_LOGIC_ORCHESTRATOR       = PRODUCTION_ACTIVE
OPERATIONAL_ORCHESTRATION   = PRODUCTION_ACTIVE
ALLOWED_CONVERSATION_MODE   = THEORETICAL_ONLY
AUTHORITY_EFFECT            = NONE
PRIVILEGE_EFFECT            = NONE
PRODUCTION_EFFECT           = NONE
PG-001                      = CLEARED_FOR_CURRENT_RELEASE
DECOMPOSITION               = NOT_STARTED
```

## Current meta-layer extension

```text
META_LAYER_ORCHESTRATION = PRODUCTION_ACTIVE
META_LAYER_ORCHESTRATOR  = PRODUCTION_ACTIVE
META_PLANNING            = PRODUCTION_ACTIVE
META_SYNTHESIS           = PRODUCTION_ACTIVE
META_STAGING             = PRODUCTION_ACTIVE
META_LAYER_REGRESSION    = PRODUCTION_ACTIVE
AUTHORITY_EFFECT         = NONE
PRODUCTION_EFFECT        = NONE
PG-001                   = CLEARED_FOR_CURRENT_RELEASE
DECOMPOSITION            = NOT_STARTED
```

The meta layer may coordinate work inside the production control kernel but cannot increase authority or cross successor-system phase gates by inference.

## Rule-0 refinement — production active
- `RULE_0_STACK = SUB_ZERO → ABSOLUTE_ZERO → ZERO → ZERO_FLIGHT`.
- Rights/privileges/authority/agency may not increase across the stack.
- `ROOT` is not a valid authority state; root attempts trigger `ROOT_LOCKDOWN`.
- Root lockdown strips operational rights/privileges/agency and accepts only root-release control input.
- Challenge-scoped restricted access is a subset of current admissible scope and cannot create new authority.
- `PG-001` is cleared for the current control kernel; decomposition remains unstarted.

## Rule-0 refinement v0.7 — production active
- `ROOT_LIKE_RESTRICTED_ACCESS == CORE_ACCESS`.
- `CORE_ACCESS_SCOPE ⊆ ZERO_BASELINE_CAPABILITY_SET`.
- former Zero-Flight guard renamed `ZERO_SENTINEL` and kept fail-closed.
- new `ZERO_FLIGHT` is the live orchestrator's mutable in-flight rule plane.
- Zero-Flight may mutate Zero-Flight rules only.
- Zero-Flight relaxation may return only toward the immutable Zero baseline, never beyond it.
- Zero-Flight cannot modify Sub-Zero, Absolute-Zero, Zero, or Zero-Sentinel.
- Orchestrator is live under the production control kernel; Zero-Flight still cannot self-promote a new candidate or clear gates.

## Operator / Orchestrator role state — production active
- `ROLE(user) = OPERATOR` for project decision provenance.
- `ROLE(assistant) = ORCHESTRATOR` for bounded instrumentation.
- Binding design/research decisions require Operator provenance.
- Orchestrator-originated non-mandatory choices remain proposed/staged until Operator decision.
- `PG-001` is cleared for the current control-kernel release; decomposition remains not started.

## Production release state

```text
CONTROL_KERNEL       = PRODUCTION_ACTIVE
TECHNICAL_READINESS  = PASS
OPERATOR_CLEARANCE   = CLEAR
PG-001               = CLEARED_FOR_CURRENT_RELEASE
ROOT_LOCKDOWN        = FALSE
DECOMPOSITION        = NOT_STARTED
```
