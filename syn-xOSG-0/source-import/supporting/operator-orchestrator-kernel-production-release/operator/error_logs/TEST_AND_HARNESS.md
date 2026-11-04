# Test & Harness Error Log

## ERR-TH-001 — Harness tests only expected inputs

- **Status:** CORRECTED IN BASELINE
- **Severity:** HIGH
- **Evidence class:** historical progression
- **Failure:** deterministic happy-path tests can miss parser/type and adversarial-input defects.
- **Control:** pair deterministic suite with loose/fuzzy/adversarial suite.

## ERR-TH-002 — Harness pass mistaken for architectural proof

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Failure:** test success is treated as evidence that the specification itself is correct.
- **Invariant:** tests demonstrate behavior against assertions; they do not prove the chosen requirements are wise or complete.

## ERR-TH-003 — Crash-only fuzz oracle

- **Status:** ACTIVE CONTROL
- **Severity:** MEDIUM
- **Failure:** fuzzy testing considers only crashes and misses invalid silent acceptance.
- **Control:** fuzz oracles must check semantic invariants, controlled rejection, timeouts, and state integrity in addition to crashes.
