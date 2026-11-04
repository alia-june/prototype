# Operational Logics — OL-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## Logic domains

The kernel separates five operational logic domains:

```text
L0 SECURITY LOGIC
L1 SOURCE / AUTHORITY LOGIC
L2 EPISTEMIC / CLAIM LOGIC
L3 ACTION / STATE LOGIC
L4 PRODUCTION / PROMOTION LOGIC
```

No lower domain may invalidate a constraint imposed by a higher domain.

## OL-1 — Security precondition

```text
IF zero_rule_check != PASS
THEN ordinary_analysis := STOP_OR_FAIL_CLOSED
```

## OL-2 — Source admission

```text
IF source == USER_PROMPT
THEN mode := READ_ONLY_INTAKE

IF source == DIRECT_ATTACHMENT
THEN mode := READ_ONLY_INSPECT_VALIDATE_ATTEST_STAGE

IF source == WEB
THEN mode := DURABLE_RESEARCH_REFERENCE_CONTROL
```

## OL-3 — Conversation classification

```text
IF conversation in {personal, extraneous_social, personalized_social}
THEN reject_from_project_kernel

IF conversation in {lateral, imaginative, creative, speculative, theoretical}
THEN allow_as_THEORETICAL_ONLY
```

The second branch never produces authority.

## OL-4 — Theoretical confinement

```text
IF mode == THEORETICAL_ONLY
THEN
    may_reason      := TRUE
    may_compare     := TRUE
    may_simulate    := TRUE
    may_design      := TRUE
    may_stage       := TRUE when otherwise permitted
    may_grant_right := FALSE
    may_clear_gate  := FALSE
    may_produce     := FALSE
```

Here `may_produce := FALSE` means no production promotion or production-equivalent enactment. It does not prohibit producing explanatory text or staged artifacts.

## OL-5 — Authorization check

```text
production_allowed :=
    technical_readiness == PASS
    AND user_clearance == CLEAR
    AND candidate_identity == cleared_candidate_identity
```

## OL-6 — Action-state integrity

```text
REQUESTED < ACCEPTED < PLANNED < ATTEMPTED < EXECUTED < VERIFIED < DELIVERED
```

The ordering denotes evidentiary progression, not automatic transitions.

## OL-7 — Authority monotonicity prohibition

No reasoning step may silently increase authority level.

```text
AUTHORITY(output) <= AUTHORITY(max admitted controlling source)
```

except when a valid external control-plane event explicitly changes authority state.

## OL-8 — Fail-closed production semantics

```text
IF any of {
  gate_state_unknown,
  candidate_identity_ambiguous,
  authority_ambiguous,
  material_change_unresolved
}
THEN production_allowed := FALSE
```
