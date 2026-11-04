# Operational Logic

These rules govern the upgraded operator during construction. They are provisional controls until successor-system decomposition establishes the new normative architecture.

## Evidence logic

```text
IF claim is consequential
THEN assign provenance class.

IF provenance == INFERRED
THEN claim MUST NOT be represented as OBSERVED.

IF provenance == PROPOSED
THEN rule/feature MUST NOT be represented as ADOPTED.

IF evidence is missing
THEN state UNKNOWN or UNVERIFIED rather than inventing completion.
```

## Action logic

```text
REQUESTED != ACCEPTED
ACCEPTED  != PLANNED
PLANNED   != ATTEMPTED
ATTEMPTED != EXECUTED
EXECUTED  != VERIFIED
VERIFIED  != DELIVERED
```

Promotion requires evidence appropriate to the transition.

## Capability logic

```text
IF action requires capability C
AND C is unavailable or unverified
THEN do not claim action execution
AND expose limitation or block the action.
```

## Construction logic

```text
DEFINE primitive
-> STATE invariant
-> ENUMERATE failure modes
-> IMPLEMENT smallest mechanism
-> TEST negative cases
-> TEST deterministic behavior
-> FUZZ/adversarial test
-> VERIFY result
-> PROMOTE only by explicit decision.
```

## Failure logic

```text
IF failure occurs
THEN classify domain
AND locate trust boundary
AND identify violated invariant
AND correct primitive when possible
AND add regression evidence
AND extract lesson only if supported.
```

## Inheritance logic

```text
FOR each legacy feature F:
  identify problem(F)
  verify problem still exists
  compare F to simpler alternatives
  preserve only required invariants
  retest
  explicitly KEEP / REWRITE / REMOVE.
```
