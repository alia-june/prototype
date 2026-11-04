# Goal-Scaffolding Release Attestation — v0.10.0

**Scope:** xOSG-0 goal-scaffolding production revision.

This attestation is derived from deterministic package evidence and the full candidate regression suite. It attests package-local identity, listed test outcomes, scaffold payload-preservation behavior, exact-descriptor lookup behavior, and final gate state.

## Release invariants

```text
TOKEN_SPELLING != TOKEN_SEMANTICS
CORE_ACCESS != PRIVILEGE
WRAPPING != EXECUTION
DESCRIPTOR != PERMISSION
PAYLOAD_AFTER == PAYLOAD_BEFORE
UNKNOWN_DESCRIPTOR -> UNRESOLVED
```

## Validation evidence

- prompt scaffolding regression: 12/12 PASS;
- production release regression: 11/11 PASS;
- full candidate regression suite: PASS;
- candidate SHA-256 verification: PASS;
- final production gate: `LOCKED_POST_RELEASE`.

## Scope limitation

This attestation does not certify external-system state, universal correctness, or the truth of every prose statement. It attests the listed package-local checks and release state.
