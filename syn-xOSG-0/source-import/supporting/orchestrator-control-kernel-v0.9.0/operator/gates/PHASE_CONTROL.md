# Phase-Control Policy

## Purpose
Prevent the Orchestrator from moving the project forward merely because a plausible next step exists.

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
PHASE = CONTROL_KERNEL_PRODUCTION_ACTIVE
DECOMPOSITION = NOT_STARTED
PRODUCTION = ACTIVE_FOR_CONTROL_KERNEL
```

## Source-stack staging status

The source/security-preference stack is active in the production control kernel. This does not begin successor-system decomposition; that remains a separate Operator-directed phase.
