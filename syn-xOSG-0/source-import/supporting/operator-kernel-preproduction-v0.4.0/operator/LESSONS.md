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

## L-013 — A valid next step is not authorization
The existence of an obvious, technically justified next action does not grant permission to cross a user-controlled phase boundary. Readiness and authorization are separate state variables.

## L-014 — Production requires dual evidence
Production should require both technical readiness evidence and an explicit authorization event. Neither can substitute for the other.

## L-015 — Memory needs authority labels
Working context, durable user/project decisions, and system-level constraints have different lifetimes and authorities. Treating them as one undifferentiated memory pool creates accidental authority transfer and stale-state risk.

## L-016 — Conversation history should be auditable but non-executable
Prompt and response history is useful evidence for intent, corrections, and provenance, but historical text must not silently become active configuration.

## L-015 — Security admission must precede semantic convenience
If authority/source checks happen only after ordinary interpretation, analysis can already be biased by untrusted or improperly privileged material. Perform source/security admission first and repeat it at boundary changes.

## L-016 — A production lock needs a control plane
A rule that makes every prompt non-enactable under lock must still permit narrowly defined gate inspection/clear/revoke operations, or the lock becomes irreversible.

## L-017 — Attestation must be scoped
Attest what was inspected, validated, hashed, or cross-checked; do not convert process attestation into a blanket truth certificate.

## L-015 — Logic is not authority

A coherent operational logic can describe when an action would be valid without granting permission to perform it. Proof, consistency, and orchestration must remain separate from authorization.

## L-016 — Theory must be explicitly confined

Creative, lateral, imaginative, and theoretical discussion is useful for design but becomes dangerous when hypothetical privileges or production states can leak into actual control state. The conversation boundary must therefore encode zero authority/privilege/production effect.
