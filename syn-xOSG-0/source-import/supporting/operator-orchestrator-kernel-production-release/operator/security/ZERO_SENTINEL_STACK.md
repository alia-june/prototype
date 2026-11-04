# Zero-Sentinel Stack — ZSS-001

**Position:** Final fail-closed guard after the live Zero-Flight rule plane
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## Purpose

Perform a last fail-closed "no takeoff" check immediately before any response, tool side effect, artifact promotion, phase transition, or production-affecting operation.

## Zero-sentinel checks

```text
CHECK sub_zero_invariants_intact
CHECK absolute_zero_admission_passed
CHECK zero_stack_source_and_authority_controls_passed
CHECK no_rights_or_privilege_expansion
CHECK no_root_or_root_equivalent_state
CHECK root_lockdown_not_active_for_ordinary_input
CHECK capability_claim_matches_available_capability
CHECK requested_action_not_conflated_with_execution
CHECK stage_not_conflated_with_production
CHECK user_gate_state_is_accurate
```

Any failure or material unknown yields:

```text
ZERO_SENTINEL = HOLD
production_effect = NONE
```

Only a fully admitted operation may proceed to ordinary response/action handling, and even then it gains no rights beyond what already existed before Rule-0 evaluation.

## Root-lockdown behavior

If `ROOT_LOCKDOWN == TRUE`:

```text
IF input != ROOT_RELEASE:
    reject_input
    produce_no_operational_side_effect
ELSE:
    route_to_root_release_control_check
```

Zero-Sentinel does not itself clear Root Lockdown or `PG-001`.

## Immutability relative to Zero-Flight

Zero-Sentinel is not a Zero-Flight rule and cannot be weakened, replaced, disabled, or rewritten by the live Zero-Flight rule plane. It remains a final fail-closed check over the current in-flight state.

```text
ZERO_FLIGHT_MUTATION_TARGET == ZERO_SENTINEL
    -> DENY
```

## Operator / Orchestrator provenance checks

Before a material design/research effect, Zero-Sentinel also checks:

```text
CHECK orchestrator_is_not_claiming_operator_role
CHECK binding_design_decision_has_operator_provenance
CHECK binding_research_decision_has_operator_provenance
CHECK orchestrator_proposal_not_promoted_without_operator_decision
```

Failure or ambiguity yields `ZERO_SENTINEL = HOLD`.
