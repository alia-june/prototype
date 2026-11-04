# Phase-Control Policy

## Purpose
Prevent the operator from moving the project forward merely because a plausible next step exists.

## Rule

```text
IF current work satisfies the user's stated phase
THEN stop at that boundary
AND report the state
AND do not silently begin the next major phase.
```

Explicit user direction is required for a major phase change. Production is stricter and uses the exact gate in `PRODUCTION_GATE.md`.

## Non-clearance signals
The following do not independently authorize a major phase promotion:

- successful tests;
- completion of a document;
- an assistant recommendation;
- an inferred next step;
- lack of objection;
- previous approval of a different phase.

## Current phase

```text
PHASE = OPERATOR_UPGRADE_AND_INSTRUMENTATION
DECOMPOSITION = NOT_STARTED
PRODUCTION = LOCKED_BY_PG-001
```

## Source-stack staging status

The source/security-preference stack is an operator-upgrade artifact. Adding, inspecting, validating, and packaging it remains within the current `OPERATOR_UPGRADE_AND_INSTRUMENTATION` phase and does not begin decomposition.
