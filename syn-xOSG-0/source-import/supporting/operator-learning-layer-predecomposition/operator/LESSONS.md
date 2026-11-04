# Lessons

Lessons are durable conclusions extracted from concrete evidence. They are not automatically normative requirements.

## L-001 — Validate structure before semantics
Malformed persistence showed that semantic checks are irrelevant if parsing, root type, or nested container types are not controlled first.

## L-002 — Fail closed at trust boundaries
Corruption, invalid recovery material, impossible state, or unverified capability should not be repaired into a trustworthy-looking success state.

## L-003 — A request is not evidence of execution
Natural language supplies intent. Execution, verification, and delivery require separate evidence.

## L-004 — Persistence spanning multiple files needs transaction semantics
Atomic replacement of each file individually does not guarantee logical atomicity across the pair.

## L-005 — Recovery data is another input surface
A transaction journal cannot be privileged merely because it was written by the runtime; it must be hashed, parsed, typed, and validated before replay.

## L-006 — Fuzzing should attack assumptions, not only syntax
The most useful fuzzy cases were structurally plausible but semantically hostile: nulls, wrong roots, controls, truncation, sequence disorder, and state mutations.

## L-007 — Tests are evidence, not specification
A green suite demonstrates conformance to encoded expectations. It does not establish that those expectations are sufficient, minimal, or conceptually correct.

## L-008 — Historical artifacts are evidence, not authority
Legacy design decisions should be requalified during migration. Age and compatibility pressure do not justify retention.

## L-009 — Provenance classes reduce epistemic drift
Separating observed, derived, inferred, proposed, unknown, and unverified prevents narrative certainty from outrunning evidence.

## L-010 — Keep normative rules separate from their representations
Machine configuration, formal logic, prompts, novice language, runtime code, and tests should have explicit derivation relationships rather than becoming peer sources of truth.

## L-011 — Failure is an architectural sensor
A failure identifies a boundary, hidden assumption, or violated invariant. Correct the primitive before adding surface-level patches.

## L-012 — Simplicity must be tested too
A smaller design is preferable only when it preserves required invariants and failure behavior. Minimalism without boundary tests can be as unsafe as overengineering.
