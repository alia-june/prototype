# 06 — Deterministic Offload

## Pressure
Validation, hashing, inventory, attestation, and repeatable orchestration do not all require semantic model inspection.

## Added
- Gestalt Hypervisor;
- deterministic task graph;
- minimum-sufficient deterministic tasks;
- data-touch minimization;
- hash and attestation mechanisms;
- scoped evidence returned for synthesis.

## Path

```text
OPERATOR DECISION
 -> ORCHESTRATOR INTENT
 -> DETERMINISTIC TASK
 -> MINIMIZED EVIDENCE
 -> META-SYNTHESIS
 -> SENTINEL
 -> REPORT
```

## Growth principle
Move a function out of probabilistic reasoning when its semantics can be made deterministic and inspectable.

## New pressure
Compact goals and symbolic notation need deterministic context without accidental semantics.

That produces **07 — Goal Scaffolding**.
