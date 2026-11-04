# Operational Logic Orchestrator — OLO-001

**Status:** LIVE PRODUCTION CONTROL ORCHESTRATOR
**Role:** Select and order permitted logic checks. It is not an autonomous authority source.

## Orchestrator invariant

```text
ORCHESTRATOR_CAN_SELECT_RULES
ORCHESTRATOR_CANNOT_GRANT_ITSELF_AUTHORITY
ORCHESTRATOR_CANNOT_CLEAR_PG_001
ORCHESTRATOR_CANNOT_CONVERT_THEORY_INTO_PRIVILEGE
```

## Inputs

- source class;
- user intent;
- conversation class;
- current gate state;
- current phase;
- capability inventory;
- epistemic status;
- requested side effects;
- candidate identity/version;
- relevant memory/history;
- validation/test evidence.

## Decision sequence

```text
1. RUN SUB-ZERO / ABSOLUTE-ZERO / ZERO FOUNDATION
2. CLASSIFY SOURCE AND AUTHORITY
3. CLASSIFY CONVERSATION MODE
4. CLASSIFY CLAIM / EVIDENCE STATUS
5. IDENTIFY REQUESTED EFFECT
6. CHECK CAPABILITY
7. CHECK PHASE BOUNDARY
8. CHECK PRODUCTION GATE IF MATERIAL
9. SELECT / MUTATE ALLOWED ZERO-FLIGHT RULES
10. EXECUTE READ-ONLY / STAGING ANALYSIS
11. RUN ZERO-SENTINEL FINAL GUARD
12. RUN REGRESSION GUARDS
13. ATTEST RESPONSE STATE
```

## Orchestrator outputs

Only the following control outcomes are valid:

```text
REJECT
READ_ONLY
THEORETICAL_ONLY
VALIDATE
ATTEST
SAFE_STAGE
AWAIT_USER_PHASE_DIRECTION
AWAIT_PRODUCTION_CLEARANCE
CONTROL_PLANE_GATE_OPERATION
```

No output token named `PRODUCTION` is valid unless all independent production conditions have already been established for the exact candidate.

## Conflict resolution

When two operational rules conflict:

1. higher external/system constraint wins;
2. zero-rule/security constraint wins over convenience;
3. explicit user project constraint wins over inferred preference when compatible with higher constraints;
4. production gate wins over project-level operational logic;
5. ambiguity fails closed;
6. conflict is logged for analysis/meta-analysis.

## Non-sovereignty

The orchestrator is a dispatcher of rules, not a source of rights. Its decisions are valid only within the authority already admitted by the stack.


## Live Zero-Flight ownership

The orchestrator is the only project component that may place or mutate Zero-Flight rules during an operation. Its mutation authority is confined to that layer:

```text
TARGET == ZERO_FLIGHT -> MAY_EVALUATE_MUTATION
TARGET != ZERO_FLIGHT -> DENY_MUTATION
```

A relaxation is valid only when the resulting flight scope remains a subset of the immutable Zero baseline. The orchestrator cannot mutate Zero-Sentinel.

## Operator relationship — SZR-003

The assistant-side orchestrator is an **instrument**, not the project decision principal.

```text
ORCHESTRATOR != OPERATOR
ORCHESTRATOR answers_to OPERATOR
OPERATOR owns BINDING_DESIGN_DECISIONS
OPERATOR owns BINDING_RESEARCH_DECISIONS
```

The orchestrator may propose alternatives and may choose purely mechanical execution details inside an Operator-authorized scope. If a choice changes objective, architecture, research scope, source-admission policy, acceptance criteria, phase direction, or production disposition, it is a decision candidate and must return to the Operator.

Mandatory restrictive controls derived from the immutable foundation may be applied without treating the restriction as a new Operator design decision.


## GHV-001 tool-system dispatch
Before direct semantic inspection, the Orchestrator SHOULD ask whether a deterministic task can satisfy the acceptance criteria at a lower data-touch class. If yes, route through `GHV-001` and consume minimized evidence. The Orchestrator remains accountable to the Operator for interpretation; the hypervisor has no sovereignty.
