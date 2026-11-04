# Meta-Orchestration System — MOS-001

MOS-001 coordinates planning, deterministic task composition, tool routing, validation, synthesis, staging, and attestation while preserving the Operator/Orchestrator boundary.

## Layers

```text
OPERATOR AGENCY
  -> META-PLANNING
  -> TASK COMPOSITION
  -> GESTALT HYPERVISOR
  -> DETERMINISTIC HEURISTICS
  -> TOOL EXECUTION
  -> EVIDENCE REDUCTION
  -> META-SYNTHESIS
  -> META-STAGING
  -> ZERO-SENTINEL
```

## Meta-orchestration contract

MOS-001 may:
- compose bounded tasks from an Operator objective;
- choose among pre-admitted deterministic heuristics;
- establish task dependencies;
- rerun deterministic validators;
- aggregate minimized evidence;
- stage a candidate and attestation.

MOS-001 may not:
- create a new project objective;
- make a binding design or research decision;
- expand tool permissions;
- increase data-touch class without a recorded reason;
- clear a production gate;
- create autonomous background execution.

## Deterministic preference

```text
IF deterministic_heuristic_satisfies_acceptance_criteria
THEN use heuristic
ELSE return bounded exception to Orchestrator
```

The Orchestrator handles only the residual work that cannot be resolved mechanically.
