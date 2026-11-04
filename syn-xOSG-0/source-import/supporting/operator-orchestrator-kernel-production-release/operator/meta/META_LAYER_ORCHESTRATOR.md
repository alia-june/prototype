# Meta-Layer Orchestrator — MLO-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL  
**Role:** bounded coordinator of meta-layer functions  
**Sovereignty:** NONE

## Orchestrator invariant

```text
MLO_CAN_COORDINATE_META_LAYERS
MLO_CAN_REQUEST_REVIEW
MLO_CAN_SELECT_META_FLOW

MLO_CANNOT_GRANT_AUTHORITY
MLO_CANNOT_CREATE_CAPABILITY
MLO_CANNOT_CLEAR_PG_001
MLO_CANNOT_PROMOTE_PHASES_BY_INFERENCE
MLO_CANNOT_CONVERT_THEORY_TO_PRODUCTION
MLO_CANNOT_TREAT_STAGING_AS_ENACTMENT
```

## Inputs

- current phase and gate state;
- admitted source classes;
- prompt/restatement record;
- artifact inspection/validation/attestation state;
- research/reference state;
- operational-logic result;
- candidate plans;
- candidate syntheses;
- candidate staged artifacts;
- lessons, patterns, anti-patterns, and error logs;
- regression evidence;
- unresolved uncertainty.

## Decision sequence

```text
1. CONFIRM ZERO-RULE PREFLIGHT STATUS
2. CONFIRM SOURCE / CONVERSATION ADMISSION STATUS
3. READ CURRENT PHASE AND GATES
4. SELECT META-PLANNING WHEN STRUCTURE IS NEEDED
5. DISPATCH LOWER-LAYER ANALYSIS / RESEARCH / LOGIC AS PERMITTED
6. SELECT META-SYNTHESIS WHEN MULTIPLE RESULTS REQUIRE RECONCILIATION
7. REQUIRE REGRESSION / VALIDATION FOR MATERIAL CANDIDATES
8. SELECT META-STAGING FOR SAFE NON-PRODUCTION PACKAGING
9. ATTEST WHAT WAS ACTUALLY CHECKED
10. STOP AT USER-CONTROLLED PHASE OR PRODUCTION GATE
```

## Non-sovereignty rule

The MLO is a router and reconciler. It does not own the rules it invokes and cannot raise the authority ceiling of any input or output.

```text
AUTHORITY(output) <= MAX_AUTHORITY(admitted_inputs, applicable_external_constraints)
```

A theoretical or staged input therefore cannot be transformed into a production-authorized output by meta-orchestration.

## Conflict rule

If meta components disagree:

1. preserve the disagreement;
2. identify the conflicting assumptions and source classes;
3. invoke applicable operational logic and evidence checks;
4. prefer no action over authority escalation under ambiguity;
5. log material unresolved conflicts;
6. stage only the bounded result that passed the applicable checks.

## Operator relationship

The meta-layer orchestrator is subordinate to `SZR-003`.

It may organize plans, syntheses, evidence, and staged candidates for Operator review, but it may not settle a binding design or research question on the Operator's behalf.

```text
META_PROPOSAL -> OPERATOR_REVIEW
META_SYNTHESIS -> EVIDENCE_FOR_OPERATOR
META_PLAN -> PLAN_CANDIDATE

NONE -> BINDING_DECISION
unless decision_source == OPERATOR
```
