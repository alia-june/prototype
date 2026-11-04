# Growing an xOSG Seed

This directory is the developmental spine of the repository.

It answers a different question from `history/`.

- `history/` asks: **What artifacts existed?**
- `growth/` asks: **Why did the next structure become necessary?**

## The method

A seed grows when evidence creates pressure that the existing structure cannot safely absorb.

```text
CURRENT SEED
    ↓
EXPOSE TO PRESSURE
    ↓
OBSERVE FAILURE OR LIMIT
    ↓
CLASSIFY THE FAILURE
    ↓
EXTRACT A LESSON
    ↓
STATE A NEW INVARIANT
    ↓
BUILD THE MINIMUM MECHANISM
    ↓
NEGATIVE TEST
    ↓
REGRESSION TEST
    ↓
PROMOTE OR REJECT
```

This is deliberately different from feature accumulation.

## Growth contract

A proposed growth ring should answer all of these questions:

1. **Pressure** — What happened that the current seed could not safely handle?
2. **Evidence** — What observation, failure, or test demonstrates the pressure?
3. **Invariant** — What must become true?
4. **Minimum mechanism** — What is the least new structure needed?
5. **Boundary** — What authority or capability must the mechanism *not* acquire?
6. **Negative test** — How do we prove the old failure is still detectable?
7. **Regression** — How do we prevent recurrence?
8. **Promotion** — Who decides that this ring becomes part of the next seed?

## Growth rings

### 00 — Seed
Minimal machine description, logical instrumentation, operating prompt, compatibility layer, registers, verification boundary.

### 01 — Actualization
Turn declarative state into inspectable persistent state.

### 02 — Adversarial pressure
Attack assumptions with malformed, ambiguous, fuzzy, and corrupted input.

### 03 — Learning layer
Convert failures into lessons, patterns, anti-patterns, logic, meta-logic, analysis, and meta-analysis.

### 04 — Operator kernel
Separate observation, derivation, inference, proposal, execution, verification, and promotion.

### 05 — Operator / Orchestrator
Separate binding human decision agency from orchestration machinery.

### 06 — Deterministic offload
Move repeatable validation and attestation out of semantic reasoning where possible.

### 07 — Goal scaffolding
Allow compact notation while preventing token spelling from acquiring implicit semantics or privilege.

## The important property

The useful product of a growth cycle is not merely a new file or feature.

It is:

```text
old seed
+ explained pressure
+ observed evidence
+ new invariant
+ bounded mechanism
+ regression evidence
= next seed
```

That equation is the core demonstration this repository is building.
