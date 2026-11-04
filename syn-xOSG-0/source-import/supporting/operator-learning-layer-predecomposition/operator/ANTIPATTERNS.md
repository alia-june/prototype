# Anti-Patterns

## AP-001 — Narrative completion
Saying an action occurred because the conversation proceeded as if it had occurred.

## AP-002 — Schema-after-access
Dereferencing nested values before validating their container and type.

## AP-003 — Silent reset on corruption
Replacing malformed persistent state with defaults and continuing as though nothing happened.

## AP-004 — Green-suite absolutism
Treating 100% passing tests as proof of correctness, completeness, security, or architectural quality.

## AP-005 — Compatibility worship
Retaining a weak primitive to avoid migration work even when the rebuild is explicitly ground-zero.

## AP-006 — Prompt-as-runtime
Treating textual instructions as though they create persistence, external actions, locks, transactions, or privileges.

## AP-007 — Representation drift
Maintaining multiple prose/JSON/prompt descriptions that independently evolve and contradict one another.

## AP-008 — Patch stacking
Responding to every defect by adding another wrapper, flag, or layer instead of questioning the primitive that enabled the defect.

## AP-009 — Recovery exceptionalism
Trusting backup, journal, cache, or recovery data more than ordinary input without validation.

## AP-010 — Premature abstraction
Generalizing from one incident before there is enough evidence to identify the real recurring structure.

## AP-011 — Self-confirming analysis
Choosing tests, interpretations, and evidence that validate the current design while not constructing meaningful falsification attempts.

## AP-012 — Hidden authority transfer
Allowing a lower-level interface, helper, compatibility layer, or user phrasing to silently expand privileges or override higher-level constraints.
