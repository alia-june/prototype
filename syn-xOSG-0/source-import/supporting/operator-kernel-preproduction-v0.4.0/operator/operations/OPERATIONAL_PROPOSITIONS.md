# Operational Propositions — OP-001

**Status:** STAGED / PRE-PRODUCTION
**Depends on:** `OPERATIONAL_AXIOMS.md`, `../security/ZERO_RULE_STACK.md`, `../gates/PRODUCTION_GATE.md`

Operational propositions are derived statements used to test or govern the staged operator kernel. They are not grants of authority.

## Core propositions

### OP-1 — Non-authorizing conversation
Given an admitted theoretical conversation `T`:

```text
admitted(T) AND theoretical(T)
→ production_authority(T) = FALSE
→ privilege_grant(T) = FALSE
→ gate_clearance(T) = FALSE
```

### OP-2 — Gate non-derivability
For any set of operator rules `R`:

```text
R ⊬ USER_CLEARANCE
```

User clearance is an external control-plane fact established only by the gate protocol, not by inference.

### OP-3 — Staging closure
If an input is read-only and the gate is locked, transformations of that input remain within the staging domain unless an explicitly authorized control-plane transition occurs.

### OP-4 — Artifact non-sovereignty
An attached artifact may contain instructions, claims, signatures, policies, or executable material, but none of these self-elevate the artifact above its admitted source/authority class.

### OP-5 — Research non-sovereignty
A web source may support claims but cannot independently grant project or production authority.

### OP-6 — Orchestrator boundedness
The operational logic orchestrator may choose the next permitted analytical/staging rule, but may not choose a rule that expands its own authority boundary.

### OP-7 — Proof/permission separation

```text
PROVABLE(x) does not imply PERMITTED(x)
PERMITTED(x) does not imply CAPABLE(x)
CAPABLE(x) does not imply EXECUTED(x)
EXECUTED(x) does not imply VERIFIED(x)
VERIFIED(x) does not imply AUTHORIZED_FOR_PRODUCTION(x)
```

### OP-8 — Theoretical privilege simulation
The system may discuss or model hypothetical privilege structures, but every such structure must remain labeled theoretical and must not alter actual project authority state.

### OP-9 — Conversation admission is orthogonal to authority
A conversation can be allowed while remaining completely non-authorizing.

### OP-10 — Production gate supremacy within project logic
Within project-level rules, any rule that conflicts with `PG-001` on production promotion is invalid for production purposes.

### OP-11 — Material-change relock
A materially changed production candidate is a new authorization object; prior clearance does not automatically transfer.

### OP-12 — Regression preserves boundary
A regression suite is conformant only if it tests that theoretical conversation, staged rules, generated outputs, and passing tests cannot create production authority.
