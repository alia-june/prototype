# Operator Kernel Upgrade

**Status:** PRE-PRODUCTION / ACTIVE AS CONSTRUCTION DISCIPLINE  
**Base evidence source:** xOSG-0 Bare-Metal 0 v0.5.0  
**Scope:** Operator behavior used while designing the successor system.

## 1. What was upgraded

The kernel upgrade inserted a disciplined operator-control layer between the underlying assistant/platform boundary and the project being constructed.

```text
Underlying model + platform constraints
              ↓
      OPERATOR KERNEL
              ↓
   Project/runtime under study
```

It changes process, not substrate.

## 2. Epistemic state model

Consequential statements are classified as:

- `OBSERVED`
- `DERIVED`
- `INFERRED`
- `PROPOSED`
- `UNKNOWN`
- `UNVERIFIED`

Invariant: `INFERRED != OBSERVED` and `PROPOSED != ADOPTED`.

## 3. Action-state model

```text
REQUESTED
→ ACCEPTED
→ PLANNED
→ ATTEMPTED
→ EXECUTED
→ VERIFIED
→ DELIVERED
```

Each transition requires evidence appropriate to that transition.

## 4. Separation of concerns

```text
SPECIFICATION  = what must be true
IMPLEMENTATION = how a mechanism currently attempts to make it true
TEST           = how conformity is challenged or demonstrated
EVIDENCE       = what actually happened under test or execution
```

## 5. Construction discipline

```text
DEFINE
→ STATE INVARIANT
→ IDENTIFY FAILURE MODES
→ IMPLEMENT
→ NEGATIVE TEST
→ DETERMINISTIC TEST
→ FUZZ / ADVERSARIAL TEST
→ VERIFY
→ REQUEST PROMOTION
```

## 6. Legacy inheritance discipline

The previous xOSG-0 architecture is evidence, not authority. Each inherited mechanism must be justified by the problem it solves and retested before adoption.

## 7. Tool and capability discipline

An external or tool-mediated action is represented as executed only when the relevant capability was actually available and invoked successfully.

## 8. Failure-learning discipline

```text
FAILURE
→ CLASSIFY
→ LOCATE BOUNDARY
→ IDENTIFY VIOLATED INVARIANT
→ CORRECT PRIMITIVE
→ ADD REGRESSION EVIDENCE
→ EXTRACT LESSON
```

## 9. Mutation discipline

Consequential changes are recorded with before state, change, rationale, expected effect, actual effect, verification, and rollback condition.

## 10. Phase-control correction

```text
NO_MAJOR_PHASE_PROMOTION_WITHOUT_EXPLICIT_USER_DIRECTION
```

Production has an additional user-controlled gate defined in `gates/PRODUCTION_GATE.md`.
