# Capability & Action Error Log

## ERR-CA-001 — Capability assumed from intent

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Evidence class:** DERIVED
- **Failure:** user intent is treated as proof that the required capability/tool exists.
- **Invariant:** capability MUST be established independently of intent.
- **Control:** `intent -> capability required -> capability available? -> execute or expose limitation`.

## ERR-CA-002 — Simulation narrated as external execution

- **Status:** ACTIVE CONTROL
- **Severity:** CRITICAL
- **Evidence class:** DERIVED from system boundary
- **Failure:** simulated roles or reasoning are described as if external agents, people, services, or actions were actually used.
- **Invariant:** external action claims require actual external action evidence.
