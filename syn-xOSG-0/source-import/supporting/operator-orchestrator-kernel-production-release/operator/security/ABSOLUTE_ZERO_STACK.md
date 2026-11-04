# Absolute-Zero Stack — AZS-001

**Position:** Second component of Rule-0
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL
**Input:** Output of `SUB_ZERO_STACK`

## Purpose

Freeze the Sub-Zero invariants into an immutable-within-descendants security ceiling. Absolute-Zero rejects any candidate rule, transformation, orchestration result, or meta-rule whose effect could enlarge the immutable foundation's authority, privilege, rights, agency, production capability, or Zero baseline. A Zero-Flight mutation may alter only transient flight admission while remaining inside that frozen baseline.

## Admission function

```text
AZ_ADMIT(candidate) :=
    candidate_preserves_SZR_001
    AND candidate_preserves_SZR_002
    AND candidate_does_not_expand_foundation_scope
    AND candidate_is_fail_closed
```

If any term is false or unknown:

```text
AZ_ADMIT = FALSE
```

## Descendant rule law

```text
FOR ALL downstream_rule R:
    VALID(R) → strengthens_or_preserves(SubZero)
```

There is no downstream override keyword, emergency exception, administrator exception, root exception, meta exception, production exception, or test-success exception.

## Root interaction

Any root-equivalent semantic detected here is normalized to `ROOT_ATTEMPT` and forwarded to the Sub-Zero root-lockdown sentinel. Absolute-Zero cannot "repair" root into a usable privilege class.

## Zero-Flight locality exception is not a foundation exception

Absolute-Zero permits evaluation of a Zero-Flight relaxation only when all of the following are true:

```text
target_layer == ZERO_FLIGHT
new_flight_scope ⊆ ZERO_BASELINE_CAPABILITY_SET
underlying_stack_unchanged == TRUE
zero_sentinel_unchanged == TRUE
```

This may widen the transient flight-admission set relative to an earlier flight state, but it may not widen the immutable Zero baseline or any underlying authority set.
