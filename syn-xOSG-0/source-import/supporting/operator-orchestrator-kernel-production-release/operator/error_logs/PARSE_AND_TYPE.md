# Parse & Type Error Log

## ERR-PT-001 — Nullable verification object

- **Status:** VERIFIED
- **Severity:** HIGH
- **Evidence class:** OBSERVED in historical fuzzy testing
- **Actual:** `verification: null` reached code assuming an object and produced an attribute error.
- **Boundary:** load/parse/type validation.
- **Violated invariant:** nested access MUST occur only after container/type validation.
- **Correction:** v0.5.0 validates root and field types before nested access.
- **Regression requirement:** nullable and wrong-type nested values remain in deterministic and fuzzy suites.
- **Lesson:** semantic validation is too late if structural validation has not already succeeded.

## ERR-PT-002 — Truncated runtime JSON

- **Status:** VERIFIED
- **Severity:** HIGH
- **Evidence class:** OBSERVED in historical fuzzy testing
- **Actual:** truncated or empty runtime state propagated raw JSON decoder failure.
- **Boundary:** persistence parse boundary.
- **Violated invariant:** corrupted persistence MUST become a controlled invalid state, not an unhandled exception.
- **Correction:** defensive loader classifies malformed JSON and fails closed.
- **Regression requirement:** truncation at multiple offsets and malformed bytes.

## ERR-PT-003 — Truncated register JSON

- **Status:** VERIFIED
- **Severity:** HIGH
- **Evidence class:** OBSERVED in historical fuzzy testing
- **Actual:** malformed register persistence surfaced raw parser errors.
- **Boundary:** persistence parse boundary.
- **Correction:** same defensive loading and type checks as runtime state.
