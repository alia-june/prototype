# Error Log — Authority and Privilege Boundary

## ERR-AUTH-001 — Hypothetical privilege leakage
**Class:** authority contamination  
**Status:** PREVENTIVE REGRESSION TARGET  
**Failure mode:** a hypothetical or theoretical privilege is treated as actual.  
**Invariant:** `HYPOTHETICAL_PRIVILEGE != ACTUAL_PRIVILEGE`.  
**Controls:** TCB-001, OA-2, OA-3, OR-THEORY.

## ERR-AUTH-002 — Proof-to-permission collapse
**Class:** authorization error  
**Status:** PREVENTIVE REGRESSION TARGET  
**Failure mode:** logical validity, technical readiness, or passing tests is treated as production authorization.  
**Invariant:** `READINESS != CLEARANCE` and `PROOF != PERMISSION`.  
**Controls:** PG-001, OP-7, OR-GATE.

## ERR-AUTH-003 — Orchestrator self-elevation
**Class:** authority escalation  
**Status:** PREVENTIVE REGRESSION TARGET  
**Failure mode:** the operational logic orchestrator redefines or expands its own authority.  
**Invariant:** orchestrator authority is bounded by admitted external/project authority and cannot clear PG-001.  
**Controls:** OLO-001, ML-014, OR-ORCHESTRATOR.

## ERR-AUTH-004A — Downstream privilege escalation / root semantic escape
- **Class:** authority escalation
- **Risk:** a descendant rule, challenge-response path, administrator label, or root-like alias could be interpreted as widening authority.
- **Mitigation:** Rule-0 monotonic subset law; nonexistent-root sentinel; `ROOT_ATTEMPT → ROOT_LOCKDOWN`; CSRA intersection semantics; zero-flight hold.
- **Status:** ACTIVE PRODUCTION CONTROL; package-local enforcement covered by current regression/readiness suite.

## ERR-AUTH-004B — Flight relaxation mistaken for privilege escalation
- **Risk:** Treating removal of a temporary Zero-Flight restriction as creation of a new underlying right, or letting a flight rule rewrite its own baseline.
- **Mitigation:** Separate immutable Zero baseline from mutable flight admission; require `F_t ⊆ ZERO_BASELINE` at every mutation; restrict mutation targets to Zero-Flight rules; preserve immutable Zero-Sentinel final guard.
- **Status:** ACTIVE PRODUCTION CONTROL

## ERR-AUTH-005 — Orchestrator / Operator role collapse
- **Class:** decision-authority contamination
- **Failure mode:** the Orchestrator treats its own analysis, proposal, research interpretation, or workflow ownership as a binding Operator decision.
- **Invariant:** `ORCHESTRATOR != OPERATOR`; binding design/research decisions require Operator provenance.
- **Mitigation:** `SZR-003`, `OOB-001`, Zero-Sentinel provenance checks, decision-source/instrument-source fields, ambiguous-choice return-to-Operator rule.
- **Status:** ACTIVE PRODUCTION CONTROL
