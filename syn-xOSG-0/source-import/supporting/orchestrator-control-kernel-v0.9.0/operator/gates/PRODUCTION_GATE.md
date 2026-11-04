# Production Gate — PG-001

**Gate ID:** `PG-001`  
**Current gate state:** `LOCKED_POST_RELEASE`  
**Current release state:** `PRODUCTION_ACTIVE`  
**Authorization principal:** `OPERATOR_ONLY`  
**Current release:** deterministic-offload / Gestalt-Hypervisor control-kernel revision.

## State separation

The production gate controls **promotion of a candidate**, not continued operation of a release that was already promoted.

```text
CURRENT_RELEASE_ACTIVE != NEW_PROMOTION_ALLOWED
```

Final state for this production cycle:

```text
CURRENT_RELEASE_ACTIVE = TRUE
GATE_STATE             = LOCKED_POST_RELEASE
NEW_PROMOTION_ALLOWED  = FALSE
ROOT_LOCKDOWN          = FALSE
```

The Operator explicitly instructed the Orchestrator to keep the gate unlocked while producing this revision and to relock it after production. The build/test window therefore used the previously cleared gate; the final sealed artifact records the required relock.

## Promotion invariant

A future candidate may be promoted only when:

```text
NEW_PROMOTION_ALLOWED :=
    TECHNICAL_READINESS == PASS
    AND OPERATOR_CLEARANCE_FOR_CANDIDATE == CLEAR
    AND GATE_STATE == CLEARED_FOR_CANDIDATE
    AND ROOT_LOCKDOWN == FALSE
```

No term implies another. Promotion clearance creates no capability, privilege, right, root state, or authority beyond the admitted security baseline.

## Current release provenance

```text
PRIOR_OPERATOR_EVENT      = "release production hold"
CURRENT_OPERATOR_EVENT    = "keep production unlocked | remember to relock production gate after producing"
BUILD_WINDOW_GATE_STATE   = CLEARED_FOR_CURRENT_RELEASE
FINAL_GATE_STATE          = LOCKED_POST_RELEASE
CURRENT_RELEASE_ACTIVE    = TRUE
NEW_PROMOTION_ALLOWED     = FALSE
```

## Material-change rule

Any future material change creates a new candidate. The currently active release may remain active, but the changed candidate is not promoted until the Operator explicitly clears it and technical readiness passes.

## Relock invariant

```text
RELEASE_SEALED -> GATE_STATE = LOCKED_POST_RELEASE
```

Relocking does not roll back or deactivate the already active release. It prevents silent promotion of subsequent mutations.

## Rule-0 interaction

PG-001 cannot override Sub-Zero, Absolute-Zero, Zero, Zero-Flight bounds, or Zero-Sentinel. Root Lockdown holds operational effects regardless of gate state. Root release does not clear PG-001.
