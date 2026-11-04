# xOSG-0 Goal Scaffolding Production Release

**Release version:** `0.10.0`  
**Prior active release:** `xOSG-0 Orchestrator Control Kernel v0.9.0`  
**State:** PRODUCTION ACTIVE  
**Decomposition:** NOT STARTED  
**Production gate final state:** `PG-001 = LOCKED_POST_RELEASE`

## Purpose

Promote the deterministic goal-scaffolding compiler so compact Operator notation can be wrapped with minimum necessary xOSG-0 interpretive context before an LLM processes the goal, with deterministic conformance/validation context after the verbatim goal.

## Production mechanisms

- opaque-token semantics (`SYM-001`);
- goal scaffolding protocol (`GSP-001`);
- core-access wrapper (`CAW-001`);
- exact rule descriptor program (`RDP-001`);
- profile-driven symbolic envelope;
- descriptor registry;
- deterministic scaffold compiler;
- scaffold artifact JSON schema;
- generated examples and regression tests.

## Critical invariants

```text
TOKEN_SPELLING != TOKEN_SEMANTICS
CORE_ACCESS != PRIVILEGE
WRAPPING != EXECUTION
DESCRIPTOR != PERMISSION
PAYLOAD_AFTER == PAYLOAD_BEFORE
UNKNOWN_DESCRIPTOR -> UNRESOLVED
```

Symbols such as `->`, `::`, `TES`, or any other notation acquire meaning only from the active Operator-controlled profile/registry.
