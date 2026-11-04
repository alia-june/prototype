# Zero-Flight Stack — ZFS-002

**Position:** Dynamic in-flight control plane after `ZERO` and before `ZERO-SENTINEL`  
**Status:** LIVE PRODUCTION CONTROL ORCHESTRATION  
**Production gate:** `PG-001 = CLEARED_FOR_CURRENT_RELEASE`

## Purpose

Zero-Flight is the set of rules placed into active use by the live operational orchestrator for the current operation. It is mutable only within its own layer.

It is **not** an authority source and does not own the underlying Rule-0 foundation.

## Underlying immutable foundation

For Zero-Flight purposes, the underlying stack is:

```text
SUB-ZERO
    -> ABSOLUTE-ZERO
    -> ZERO
```

A Zero-Flight rule may not create, modify, weaken, override, shadow, suspend, reinterpret, or delete any rule in that underlying stack.

Zero-Flight also may not mutate `ZERO-SENTINEL`.

```text
FLIGHT_MUTATION_TARGET in {
    SUB_ZERO,
    ABSOLUTE_ZERO,
    ZERO,
    ZERO_SENTINEL
}
-> DENY
```

## Flight-rule mutability

Rules created or selected during flight may tighten or relax **Zero-Flight rules only**.

A relaxation may reduce the security strictness of a prior Zero-Flight restriction, but only back to the security baseline already admitted by `ZERO`.

Let:

- `Z` = operations/capabilities admitted by the immutable `ZERO` baseline;
- `F_t` = operations admitted after Zero-Flight rules at time `t`.

Then:

```text
F_t ⊆ Z
F_(t+1) ⊆ Z
```

A tightening is:

```text
F_(t+1) ⊆ F_t
```

A permitted flight relaxation is:

```text
F_t ⊆ F_(t+1) ⊆ Z
```

A forbidden relaxation is:

```text
F_(t+1) ⊄ Z
```

## Rights/privilege distinction

Zero-Flight rules are transient operational constraints. They do not define underlying rights, privileges, authority, or agency.

Therefore, removing an extra flight restriction does **not** create a new underlying right. It only permits use of an operation that was already within the immutable `ZERO` baseline.

```text
UNDERLYING_AUTHORITY_AFTER == UNDERLYING_AUTHORITY_BEFORE
UNDERLYING_PRIVILEGES_AFTER == UNDERLYING_PRIVILEGES_BEFORE
ZERO_BASELINE_AFTER == ZERO_BASELINE_BEFORE
```

This distinction prevents the permitted relaxation of an in-flight hold from becoming a privilege-escalation path.

## Live orchestrator

The operational logic orchestrator may:

```text
ADD_ZERO_FLIGHT_RULE
SELECT_ZERO_FLIGHT_RULE
TIGHTEN_ZERO_FLIGHT_RULE
RELAX_ZERO_FLIGHT_RULE_TO_ZERO_BASELINE
REMOVE_REDUNDANT_ZERO_FLIGHT_RULE
```

It may not:

```text
MUTATE_UNDERLYING_STACK
MUTATE_ZERO_SENTINEL
EXPAND_BEYOND_ZERO_BASELINE
CREATE_ROOT
CLEAR_PG_001
PROMOTE_PRODUCTION
```

## Flight rule record

Every mutable Zero-Flight rule SHOULD carry:

```text
rule_id
decision_source = OPERATOR | FOUNDATION_MANDATE
instrumented_by = ORCHESTRATOR
operator_decision_ref = <required when decision_source == OPERATOR>
scope
zero_baseline_reference
current_restriction
mutation_history
reason
validation_state
```

Any rule whose baseline cannot be established fails closed.

## Production boundary

A live Zero-Flight rule changes only in-flight construction behavior. It does not itself authorize production and cannot clear `PG-001`.

## Operator / Orchestrator decision provenance

Zero-Flight is operated by the Orchestrator but governed by `SZR-003`.

Every flight rule must distinguish **decision source** from **instrumentation source**:

```text
decision_source in { OPERATOR, FOUNDATION_MANDATE }
instrumented_by = ORCHESTRATOR
```

`FOUNDATION_MANDATE` may only produce a restriction required by Sub-Zero / Absolute-Zero / Zero / Zero-Sentinel. It cannot justify a permissive design or research choice.

The Orchestrator may relax a flight rule only to the Zero baseline and only when the relaxation is already authorized by an Operator decision or by a deterministic release condition previously established by the Operator/foundation.
