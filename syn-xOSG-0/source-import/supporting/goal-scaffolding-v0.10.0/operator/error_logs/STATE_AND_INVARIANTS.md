# State & Invariant Error Log

## ERR-SI-001 — Requested action conflated with completed action

- **Status:** CONTAINED
- **Severity:** HIGH
- **Evidence class:** DERIVED from prior architecture and upgrade requirements
- **Risk:** natural-language requests can be narrated as completed work without execution evidence.
- **Invariant:** `requested != attempted != executed != verified != delivered`.
- **Control:** represent each stage distinctly and require evidence for promotion.

## ERR-SI-002 — Verification state detached from workflow state

- **Status:** VERIFIED
- **Severity:** MEDIUM
- **Evidence class:** OBSERVED/DERIVED from v0.5.0 hardening
- **Risk:** a `PASS` value outside verification/delivery/log states creates impossible state.
- **Invariant:** verification status MUST be compatible with workflow state.
- **Control:** validate state/verification combinations and reject impossible pairs.
