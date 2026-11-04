# Operational Logic Orchestrator — OLO-001

**Status:** STAGED / PRE-PRODUCTION
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
1. RUN ZERO-RULE PREFLIGHT
2. CLASSIFY SOURCE AND AUTHORITY
3. CLASSIFY CONVERSATION MODE
4. CLASSIFY CLAIM / EVIDENCE STATUS
5. IDENTIFY REQUESTED EFFECT
6. CHECK CAPABILITY
7. CHECK PHASE BOUNDARY
8. CHECK PRODUCTION GATE IF MATERIAL
9. SELECT ALLOWED LOGIC STACK
10. EXECUTE READ-ONLY / STAGING ANALYSIS
11. RUN REGRESSION GUARDS
12. ATTEST RESPONSE STATE
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
