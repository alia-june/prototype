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
