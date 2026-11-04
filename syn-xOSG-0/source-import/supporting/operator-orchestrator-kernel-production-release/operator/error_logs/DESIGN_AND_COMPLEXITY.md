# Design & Complexity Error Log

## ERR-DC-001 — Documentation architecture mistaken for runtime architecture

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Failure:** representations (JSON, logical prose, prompts, novice interface) become duplicated sources of authority.
- **Invariant:** representations may differ in form but authority and derivation must be explicit.

## ERR-DC-002 — Feature accumulation masquerades as progress

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Failure:** each failure leads to another layer without reevaluating primitives, increasing accidental complexity.
- **Control:** prefer deletion, simplification, or primitive correction before adding mechanisms.

## ERR-DC-003 — Abstraction before evidence

- **Status:** ACTIVE CONTROL
- **Severity:** MEDIUM
- **Failure:** a generalized mechanism is introduced before multiple concrete cases justify it.
- **Control:** capture concrete incidents first; promote a pattern only after repeated evidence or strong invariant reasoning.
