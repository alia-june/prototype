# 07 — Goal Scaffolding

## Pressure
Compact symbolic requests are useful, but symbols can acquire accidental meaning if the system treats spelling as authority.

## Added
- opaque-token semantics;
- Operator-controlled syntax profiles;
- descriptor registry;
- deterministic scaffold compiler;
- exact payload preservation;
- conformance context around a verbatim goal.

## Critical invariants

```text
TOKEN_SPELLING != TOKEN_SEMANTICS
CORE_ACCESS != PRIVILEGE
WRAPPING != EXECUTION
DESCRIPTOR != PERMISSION
PAYLOAD_AFTER == PAYLOAD_BEFORE
UNKNOWN_DESCRIPTOR -> UNRESOLVED
```

## Result
The seed can now accept compact notation while keeping meaning explicit and externally controlled.

## Next growth
The next ring should not be invented in advance. It should emerge from the next demonstrated pressure on the current seed.
