# 05 — Operator / Orchestrator Separation

## Pressure
A system that coordinates decisions can begin to look as though it owns those decisions.

## Added boundary

```text
OPERATOR
  owns binding design and research decisions

ORCHESTRATOR
  instruments, coordinates, validates, and reports
```

## Supporting controls
- monotonic non-escalation;
- phase control;
- explicit production gates;
- theory is not authority;
- proof is not permission;
- orchestration is not sovereignty.

## New pressure
The orchestration layer still touches too much data for tasks that can be deterministic.

That produces **06 — Deterministic Offload**.
