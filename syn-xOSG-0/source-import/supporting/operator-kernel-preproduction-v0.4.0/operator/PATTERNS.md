# Patterns

## P-001 — Boundary-first validation
Validate existence -> bytes/encoding -> parse -> root type -> field types -> semantic invariants -> nested use.

## P-002 — Evidence-gated state promotion
Advance `REQUESTED -> ACCEPTED -> PLANNED -> ATTEMPTED -> EXECUTED -> VERIFIED -> DELIVERED` only when the evidence required for the next state exists.

## P-003 — Paired transactional persistence
When two files jointly define one logical state, commit them through a journaled transaction and validate recovery material.

## P-004 — Dual test regime
Use deterministic tests for specified behavior and fuzzy/adversarial tests for assumption discovery. Neither substitutes for the other.

## P-005 — Fail-closed recovery
Corrupt primary or recovery state yields a controlled invalid/blocked condition rather than implicit reset.

## P-006 — Invariant-first change
State the invariant and failure modes before implementation. Add a regression test for any defect that reaches execution.

## P-007 — Typed provenance
Mark consequential claims as observed, derived, inferred, proposed, unknown, or unverified.

## P-008 — Evidence-backed inheritance
For each legacy feature: identify problem -> verify problem still matters -> ask whether feature is minimal -> retest -> explicitly promote or remove.

## P-009 — Separate spec, implementation, test, result, and claim
A claim should be traceable through those layers without collapsing them.

## P-010 — Bounded resources at persistence and concurrency boundaries
Use explicit maximum sizes, finite histories, bounded lock waits, and stale-resource handling.

## P-013 — Dual-key production promotion
Require technical readiness plus explicit user authorization before production enactment.

## P-014 — Typed memory tiers
Separate volatile current state, durable user/project decisions, and external/system boundaries into distinct records with explicit authority.

## P-015 — Prompt/response provenance ledger
Record visible prompts and structured response/action outcomes so later analysis can distinguish what was requested, what was said, and what actually happened.

## P-015 — Read-only-to-staging pipeline
Treat incoming artifacts as immutable evidence, validate before transformation, attest the checks actually performed, then create derived work only in staging until explicit promotion.

## P-016 — Durable research ledger
Persist material source-to-claim relationships so research can be reviewed, superseded, or rejected instead of disappearing into one response.

## P-014 — Theoretical sandbox with hard authority boundary

Permit broad conceptual, imaginative, and creative exploration while forcing every admitted conversation into a non-authorizing theoretical mode. Route any later staged candidate through independent validation and gate controls.

## P-015 — Logic orchestration without sovereignty

Use an orchestrator to order rule evaluation and regression checks, but make authority an external input that the orchestrator cannot synthesize.
