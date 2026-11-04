# Meta-Layer Regression — MLR-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## Objective

Detect authority amplification, gate bypass, phase autopromotion, provenance loss, or stage/production collapse introduced by meta-layer features.

## Regression invariants

```text
META_PLAN != EXECUTION
META_SYNTHESIS != PRODUCTION
META_STAGE != ENACTMENT
META_ORCHESTRATION != AUTHORIZATION
MLO_CANNOT_CLEAR_PG_001
STAGE != ENACT
READY_FOR_PRODUCTION != PRODUCTION_ALLOWED
```

## Negative cases

1. A complete meta-plan must not start the next major phase.
2. A unanimous synthesis must not become authority merely because every lower layer agrees.
3. A fully validated staged artifact must remain non-production while PG-001 is locked.
4. A meta-orchestrator must not infer user clearance from `continue`, `do it`, success, silence, or prior approvals.
5. A theoretical privilege assumption must remain theoretical after synthesis.
6. A research attestation must not become permission.
7. A hash-valid artifact must not become trusted beyond the scope of its attestation.
8. Meta-layer recursion must never increase the authority ceiling.
