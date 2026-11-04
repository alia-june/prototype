# Production Release Record — v0.10.0

**Release:** goal-scaffolding / symbolic-envelope production revision  
**Prior production release:** v0.9.0 deterministic-offload / Gestalt-Hypervisor control kernel  
**Operator clearance:** explicit `unlock production and emmit`  
**Current release:** `PRODUCTION_ACTIVE`  
**Final gate:** `PG-001 = LOCKED_POST_RELEASE`  
**Successor-system decomposition:** NOT STARTED

## Scope

This release promotes the deterministic goal-scaffolding compiler and supporting symbolic-context controls. It does not alter the Rule-0 authority ceiling, create new privileges, or start successor-system decomposition.

## Promoted components

```text
SYM-001 — opaque token semantics
GSP-001 — goal scaffolding protocol
CAW-001 — core-access wrapper
RDP-001 — exact rule descriptor program
```

Supporting artifacts include the syntax profile, descriptor registry, scaffold schema, deterministic compiler, generated examples, and regression tests.

## Critical invariants

```text
TOKEN_SPELLING != TOKEN_SEMANTICS
CORE_ACCESS != PRIVILEGE
WRAPPING != EXECUTION
DESCRIPTOR != PERMISSION
PAYLOAD_AFTER == PAYLOAD_BEFORE
UNKNOWN_DESCRIPTOR -> UNRESOLVED
```

## Promotion lifecycle

```text
STAGED_CANDIDATE
 -> OPERATOR_CLEARANCE
 -> TECHNICAL_READINESS
 -> PROMOTION
 -> RELEASE_SEAL
 -> PG-001_LOCKED_POST_RELEASE
```

Relocking prevents future promotion without deactivating v0.10.0.
