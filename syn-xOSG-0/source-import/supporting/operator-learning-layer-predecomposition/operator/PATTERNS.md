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
