# Analysis — Pre-Decomposition Operator Upgrade

## Scope
This analysis evaluates the current migration position and the lessons demonstrated by xOSG-0 through v0.5.0. It does not yet specify the successor architecture.

## Current assessment

### 1. Strongest demonstrated property: explicit failure handling
The v0.5.0 runtime's most valuable contribution is not its named orchestration roles or four-layer presentation. It is the conversion of implicit failure into explicit state: malformed persistence, impossible combinations, transaction recovery, bounded locking, input limits, and verification state are inspectable and testable.

### 2. Most reusable lesson: boundary discipline
The historical fuzzy failures occurred at boundaries where data moved from untrusted representation into assumed structure. This suggests the successor should identify trust boundaries before choosing high-level abstractions.

### 3. Potential legacy liability: duplicated representations
The four-layer architecture was useful for communicating the same workflow to machines, implementers, assistants, and novices. However, multiple manually maintained representations can become competing sources of truth. The successor should examine whether these can be derived from a smaller canonical core.

### 4. Potential legacy liability: state vocabulary may encode implementation history
The existing state machine is coherent, but its exact states and names should not be inherited without proving that they are irreducible for the new objective.

### 5. Testing maturity exceeds specification maturity
The v0.5.0 package has strong local robustness tests relative to its size. The next system should preserve that discipline while spending more effort on whether the tested invariants are the right invariants.

### 6. Migration should preserve evidence, not shape
We should preserve defect history, successful controls, tests, and boundary lessons even if none of the current top-level architecture survives.

## Questions reserved for decomposition

- What is the smallest unit of state the successor actually needs?
- Which facts require persistence versus conversational reconstruction?
- What constitutes an action, and what evidence proves it occurred?
- What must be canonical versus generated?
- Which trust boundaries exist independent of implementation language?
- What kinds of recovery are required, and from what failures?
- What is the minimal verification model?
- Which mechanisms belong to the operator and which belong to the system being built?

These are intentionally questions, not answers. Decomposition has not yet begun.
