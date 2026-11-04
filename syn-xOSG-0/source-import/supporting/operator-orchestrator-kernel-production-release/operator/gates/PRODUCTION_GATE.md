# Production Gate — PG-001

**Gate ID:** `PG-001`  
**Current state:** `CLEARED_FOR_CURRENT_RELEASE`  
**Authorization principal:** `OPERATOR_ONLY`  
**Current release scope:** operator/orchestrator control kernel represented by this package.

## Core invariant

```text
PRODUCTION_ALLOWED :=
    TECHNICAL_READINESS == PASS
    AND
    OPERATOR_CLEARANCE == CLEAR
    AND
    ROOT_LOCKDOWN == FALSE
```

No term implies another. Production clearance never creates a capability, privilege, right, root state, or authority beyond the existing security baseline.

## Technical readiness

Technical readiness may be `PASS` only when the applicable release candidate has:

1. defined scope/version identity;
2. explicit invariants;
3. known limitations recorded;
4. deterministic tests complete;
5. negative/failure-path tests complete;
6. adversarial/fuzz-style tests when applicable;
7. unresolved critical defects = 0, unless explicitly accepted by the Operator;
8. integrity/provenance records complete;
9. rollback/recovery behavior defined when production mutation is possible;
10. final verification record generated.

Readiness does not itself authorize production.

## Operator clearance

Clearance requires an **explicit Operator instruction for the current candidate**. It may not be inferred from silence, conversational momentum, successful tests, or an Orchestrator recommendation.

Canonical control commands remain:

```text
CLEAR PRODUCTION GATE PG-001
LOCK PRODUCTION GATE PG-001
```

However, because `SZR-003` makes the user-controlled Operator the binding decision principal, an unambiguous Operator directive with equivalent meaning is valid clearance. The Orchestrator must record the exact user wording and candidate scope.

## Current clearance event

```text
OPERATOR_EVENT         = "release production hold"
EVENT_SOURCE           = user / Operator
CANDIDATE_SOURCE       = pre-production v0.8.0 + release-state synchronization
TECHNICAL_READINESS    = PASS
OPERATOR_CLEARANCE     = CLEAR
ROOT_LOCKDOWN          = FALSE
PRODUCTION_ALLOWED     = TRUE
GATE_STATE             = CLEARED_FOR_CURRENT_RELEASE
```

## Revocation

The Operator may relock the gate explicitly at any time.

## Material-change reset

Any material change to production semantics, authority boundaries, persistence, safety controls, external side effects, or release contents automatically invalidates this clearance and returns the gate to `LOCKED`. Routine logging, prompt-history updates, integrity regeneration, and non-semantic documentation corrections do not themselves constitute a material semantic change.

## Rule-0 interaction

PG-001 cannot override Sub-Zero, Absolute-Zero, Zero, Zero-Flight bounds, or Zero-Sentinel. If `ROOT_LOCKDOWN` becomes active, production is held regardless of PG-001 clearance. Root release exits lockdown only; it does not independently grant production clearance.

## Scope boundary

This clearance activates the **control kernel**. `DECOMPOSITION = NOT_STARTED`; therefore no not-yet-designed successor system is implicitly promoted by this event.
