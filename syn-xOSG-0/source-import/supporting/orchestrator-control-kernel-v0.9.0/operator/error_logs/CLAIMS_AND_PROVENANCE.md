# Claims & Provenance Error Log

## ERR-CP-001 — Inference promoted to observation

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Invariant:** `INFERRED` MUST NOT silently become `OBSERVED`.
- **Control:** provenance class accompanies consequential claims.

## ERR-CP-002 — Proposal promoted to architecture without decision

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Invariant:** `PROPOSED` is not `ADOPTED`.
- **Control:** promotion requires explicit invariant, failure review, evidence/test, and decision record.

## ERR-CP-003 — Missing evidence represented as certainty

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Control:** use `UNKNOWN` or `UNVERIFIED`; do not fill gaps silently.
