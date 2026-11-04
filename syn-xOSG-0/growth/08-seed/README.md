# 08 — Seed

## Definition

Seed is the final distilled kernel produced by the developmental path that begins with ES-xOSG-7.

It is not the original system.

It is what remains after the system has been actualized, broken, studied, formalized, separated, offloaded, and reduced.

```text
ES-xOSG-7
  -> evidence
  -> failures
  -> lessons
  -> invariants
  -> boundaries
  -> deterministic mechanisms
  -> reduction
  -> SEED
```

## Admission test

A component should enter Seed only when it is:

- necessary;
- explicit;
- bounded;
- testable;
- provenance-traceable;
- non-redundant;
- compatible with the surviving invariants.

## Seed is not

- the complete archive;
- every experimental feature;
- every prompt;
- every historical implementation;
- every rule ever proposed;
- a compressed release bundle.

## Seed is

the smallest coherent package that preserves the justified architecture discovered during development.

## Extraction principle

```text
IF removing X breaks a required invariant:
    X may belong in Seed

IF X exists only for historical explanation:
    keep X in history

IF X is useful but optional:
    keep X as scaffolding

IF X duplicates another mechanism:
    reduce or remove X

IF X cannot be tested or bounded:
    do not promote it into Seed yet
```

## Final purpose

Seed should be capable of becoming a new genesis elsewhere.

That creates the full cycle:

```text
GENESIS
  ↓
DEVELOPMENT
  ↓
DISTILLATION
  ↓
SEED
  ↓
NEW GENESIS
```
