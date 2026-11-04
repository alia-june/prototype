# 04 — Operator Kernel

## Pressure
Without explicit epistemic and action states, conversation can blur what was observed, inferred, proposed, executed, or verified.

## Added

Epistemic states:

```text
OBSERVED
DERIVED
INFERRED
PROPOSED
UNKNOWN
UNVERIFIED
```

Action states:

```text
REQUESTED
 -> ACCEPTED
 -> PLANNED
 -> ATTEMPTED
 -> EXECUTED
 -> VERIFIED
 -> DELIVERED
```

Construction discipline:

```text
DEFINE
 -> STATE INVARIANT
 -> IDENTIFY FAILURE MODES
 -> IMPLEMENT
 -> NEGATIVE TEST
 -> DETERMINISTIC TEST
 -> FUZZ / ADVERSARIAL TEST
 -> VERIFY
 -> REQUEST PROMOTION
```

## Key separation

```text
SPECIFICATION != IMPLEMENTATION != TEST != EVIDENCE
```

## New pressure
Binding design authority and orchestration activity must not collapse into the same role.

That produces **05 — Operator / Orchestrator**.
