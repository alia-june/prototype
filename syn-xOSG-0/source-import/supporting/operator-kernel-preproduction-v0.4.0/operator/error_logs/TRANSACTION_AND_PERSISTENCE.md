# Transaction & Persistence Error Log

## ERR-TP-001 — Split state/register commit

- **Status:** CONTAINED
- **Severity:** HIGH
- **Evidence class:** DERIVED from persistence design
- **Risk:** state and registers can describe different logical moments if written independently.
- **Invariant:** state + registers form one logical transaction.
- **Control:** journal, canonical checksum, atomic state write, atomic register write, journal removal.

## ERR-TP-002 — Interrupted transaction recovery trusts corrupt journal

- **Status:** VERIFIED
- **Severity:** HIGH
- **Evidence class:** DERIVED and tested in v0.5.0
- **Invariant:** recovery material MUST itself be authenticated and validated.
- **Control:** verify journal checksum and validate embedded structures before replay; fail closed otherwise.

## ERR-TP-003 — Lock becomes permanent failure

- **Status:** VERIFIED
- **Severity:** MEDIUM
- **Evidence class:** DERIVED and tested in v0.5.0
- **Control:** bounded acquisition timeout, stale-lock threshold, symlink refusal, normal cleanup.
