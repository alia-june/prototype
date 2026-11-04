# Production Gate — PG-001

**Gate ID:** `PG-001`  
**Current state:** `LOCKED`  
**Authorization principal:** `USER_ONLY`  
**Applies to:** promotion/enactment of the successor system as production or production-equivalent.

## Core invariant

```text
PRODUCTION_ALLOWED :=
    TECHNICAL_READINESS == PASS
    AND
    USER_CLEARANCE == CLEAR
```

Neither term implies the other.

## Technical readiness

Technical readiness MAY be marked `PASS` only when the applicable release candidate has:

1. a defined scope and version;
2. explicit invariants;
3. known limitations recorded;
4. deterministic tests complete;
5. negative/failure-path tests complete;
6. fuzzy/adversarial testing complete when applicable;
7. unresolved critical defects = 0, unless explicitly accepted by the user;
8. integrity/provenance records complete;
9. rollback/recovery procedure defined when production mutation is possible;
10. final verification record generated.

Passing this checklist does **not** authorize production.

## User clearance

Only a direct user message containing the exact command below clears the authorization half of this gate:

```text
CLEAR PRODUCTION GATE PG-001
```

The assistant MUST NOT:

- generate the command on the user's behalf and treat that as authorization;
- infer clearance from `continue`, `looks good`, `do it`, silence, enthusiasm, or related language;
- treat successful tests as user authorization;
- treat prior clearance for a materially different candidate as current clearance.

If the exact command is received while technical readiness is not `PASS`, record `USER_CLEARANCE = REQUESTED_EARLY` and keep production blocked until readiness passes and the user re-confirms clearance for the ready candidate.

## Revocation

The user may relock the gate with:

```text
LOCK PRODUCTION GATE PG-001
```

## Material-change reset

After clearance, any material change to production semantics, authority boundaries, persistence, safety controls, external side effects, or release contents automatically invalidates the clearance and returns the gate to `LOCKED`.

## Initial state

```text
TECHNICAL_READINESS = NOT_EVALUATED
USER_CLEARANCE      = NOT_GIVEN
PRODUCTION_ALLOWED  = FALSE
```

Safe staging, validation, attestation, and read-only research do not constitute production promotion.
