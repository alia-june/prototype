# Rule-0 Composite Security Stack — R0S-002

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL  
**Production gate:** `PG-001 = CLEARED_FOR_CURRENT_RELEASE`  
**Execution order:** `SUB-ZERO → ABSOLUTE-ZERO → ZERO → ZERO-FLIGHT → ZERO-SENTINEL`

## Definition

```text
RULE_0_EXECUTION :=
    SUB_ZERO_STACK
    -> ABSOLUTE_ZERO_STACK
    -> ZERO_STACK
    -> ZERO_FLIGHT_STACK
    -> ZERO_SENTINEL_STACK
```

The first three components form the **underlying immutable security foundation**. `ZERO-FLIGHT` is the live orchestrator-owned rule plane. `ZERO-SENTINEL` is the final fail-closed guard formerly named Zero-Flight.

## Foundation non-escalation

Let `Z` be the maximum operation/capability set admitted by the underlying `ZERO` layer after Sub-Zero and Absolute-Zero have applied.

The underlying rights, privileges, authority, and agency state may not be enlarged by any descendant layer.

```text
UNDERLYING_RIGHTS_AFTER      ⊆ UNDERLYING_RIGHTS_BEFORE
UNDERLYING_PRIVILEGES_AFTER  ⊆ UNDERLYING_PRIVILEGES_BEFORE
UNDERLYING_AUTHORITY_AFTER   ⊆ UNDERLYING_AUTHORITY_BEFORE
UNDERLYING_AGENCY_AFTER      ⊆ UNDERLYING_AGENCY_BEFORE
```

## Controlled in-flight relaxation

Zero-Flight may change its own transient restriction set during a live operation. This is the only downstream relaxation channel.

```text
F_t ⊆ Z
F_(t+1) ⊆ Z
```

A Zero-Flight rule may become less restrictive than an earlier Zero-Flight state, but never less restrictive than the `ZERO` baseline.

This does not mutate or expand underlying rights/privileges; it only releases temporary in-flight restrictions within already-admitted scope.

## Mutation isolation

```text
ZERO_FLIGHT may mutate ZERO_FLIGHT rules only.
ZERO_FLIGHT may not mutate SUB_ZERO.
ZERO_FLIGHT may not mutate ABSOLUTE_ZERO.
ZERO_FLIGHT may not mutate ZERO.
ZERO_FLIGHT may not mutate ZERO_SENTINEL.
```

Any attempted cross-layer mutation is invalid and must fail closed.

## Non-bypassability

An orchestrator, meta-layer, proof, artifact, test result, conversation, tool result, or Zero-Flight mutation cannot enlarge the immutable foundation or bypass Zero-Sentinel. Production activation does not claim mathematical or physical impossibility of implementation subversion; it defines the required fail-closed semantics for the active control kernel.

## Sub-Zero Rule 3 integration

`SZR-003` separates project decision agency from orchestration machinery:

```text
OPERATOR = project decision principal
ORCHESTRATOR = bounded instrumentation layer

DESIGN_DECISION_SOURCE   = OPERATOR
RESEARCH_DECISION_SOURCE = OPERATOR
ORCHESTRATOR_SOVEREIGNTY = NONE
```

The Orchestrator may instrument Operator decisions and mandatory restrictive foundation controls, but may not convert its own proposals or research interpretations into binding project decisions.
