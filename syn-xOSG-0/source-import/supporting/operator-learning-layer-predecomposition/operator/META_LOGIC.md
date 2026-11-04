# Meta-Logic

Meta-logic governs the rules themselves: how they are created, ordered, challenged, changed, and retired.

## ML-001 — Rule admission
A new rule MAY be admitted only when at least one of the following is present:
1. a demonstrated failure or near-miss;
2. a necessary invariant derived from an explicit system objective;
3. an external constraint that actually applies;
4. repeated evidence of a beneficial pattern.

Convenience alone is insufficient for a core rule.

## ML-002 — Rule provenance
Every consequential rule SHOULD identify whether it is:
- inherited,
- evidence-derived,
- constraint-derived,
- proposed,
- experimentally promoted.

## ML-003 — Rule precedence
When rules conflict, do not silently choose one. Identify the conflict, determine their authority/source, and either resolve it by a higher-order invariant or preserve the conflict as unresolved.

## ML-004 — Falsifiability requirement
A rule that cannot be meaningfully violated, tested, or observed is probably descriptive prose rather than an enforceable invariant. Keep that distinction explicit.

## ML-005 — Minimality pressure
Before adding a rule or layer, test whether an existing invariant can be stated more precisely or an existing primitive corrected instead.

## ML-006 — No authority by representation
JSON, prose, prompts, code, schemas, tests, and generated reports do not gain authority merely through format. Authority must be explicitly assigned.

## ML-007 — No authority by repetition
A statement repeated across many documents is not more true. Duplication increases drift risk unless one representation is canonical and the others are generated or checked derivatives.

## ML-008 — Promotion and demotion are symmetric
Any promoted rule or primitive can later be demoted, rewritten, or removed when contrary evidence appears. Architecture is not append-only.

## ML-009 — Tests follow invariants, not vice versa
Tests encode expected evidence for invariants. Do not redefine the invariant merely to preserve passing tests unless the invariant itself is shown to be wrong.

## ML-010 — Meta-rules are also revisable
This document is not exempt from its own change discipline. A meta-rule can be challenged by evidence and must not become an untouchable source of accidental complexity.
