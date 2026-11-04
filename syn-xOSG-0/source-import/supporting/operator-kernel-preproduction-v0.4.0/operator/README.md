# Operator Kernel, Learning & Diagnostics Layer

**Status:** Active PRE-PRODUCTION operator overlay  
**Base:** xOSG-0 Bare-Metal 0 v0.5.0  
**Purpose:** Upgrade operator discipline and learning instrumentation before successor-system decomposition.

This directory is deliberately separate from the v0.5.0 normative source. It does not claim to modify the underlying model, hidden instructions, privileges, or external capabilities.

## Kernel and control

- `KERNEL_UPGRADE.md` — what changed in the operator and what did not.
- `gates/PHASE_CONTROL.md` — prevents implicit major-phase advancement.
- `gates/PRODUCTION_GATE.md` — user-exclusive production authorization gate (`PG-001`).

## Memory

- `memory/CURRENT_MEMORY.md` — volatile active project state.
- `memory/DURABLE_MEMORY.md` — long-lived user/project decisions.
- `memory/SYSTEM_MEMORY.md` — project-visible effective system boundaries; never a hidden-instruction dump.
- `memory/MEMORY_MODEL.md` — authority and persistence relationships.

## History

- `history/PROMPT_HISTORY.md` — visible user-prompt provenance for this migration session.
- `history/RESPONSE_LOG.md` — structured record of assistant responses, actions, corrections, and production state.

## Learning stack

1. `error_logs/`
2. `LESSONS.md`
3. `PATTERNS.md`
4. `ANTIPATTERNS.md`
5. `LOGIC.md`
6. `META_LOGIC.md`
7. `ANALYSIS.md`
8. `META_ANALYSIS.md`

## Operational logic layer

- `operations/OPERATIONAL_AXIOMS.md`
- `operations/OPERATIONAL_PROPOSITIONS.md`
- `operations/OPERATIONAL_LOGICS.md`
- `operations/OPERATIONAL_LOGIC_STACKS.md`
- `operations/THEORETICAL_CONVERSATION_BOUNDARY.md`
- `operations/OPERATIONAL_REGRESSION.md`
- `operations/OPERATIONAL_LOGIC_ORCHESTRATOR.md`
- `operations/OPERATIONAL_ORCHESTRATION.md`
- `validation/test_operational_regression.py`

The word **operational** describes operator workflow discipline. It does not grant production authority, external system control, special rights, or privileges.

## Promotion rule

No item in this directory becomes part of the successor architecture merely because it is written here. Promotion requires evidence and explicit decision. Production is separately blocked unless both technical readiness and user clearance satisfy `gates/PRODUCTION_GATE.md`.

## Current gate state

```text
DECOMPOSITION          = NOT_STARTED
TECHNICAL_READINESS    = NOT_EVALUATED
USER_CLEARANCE         = NOT_GIVEN
PRODUCTION_ALLOWED     = FALSE
PRODUCTION_GATE        = PG-001 / LOCKED
```
