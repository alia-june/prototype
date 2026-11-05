> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# External Offload Engine Integration

**Status:** `[GENERATED-PROPOSAL]` based on the separately recorded `heuristic_offload_engine_v0_2.zip`.

The engine archive is not distributed in this sanitized publication candidate. Its identity and reported license are retained in `SOURCE_RECEIPTS.json` and `THIRD_PARTY_NOTICES.md`. Any use requires obtaining and validating the engine independently.

## Use it when

The task is a bounded local command with known inputs, an explicit idempotency classification, mechanically checkable outputs, finite recovery authority, and a consequence level compatible with the engine's missing isolation controls.

Suitable examples include deterministic prompt assembly, schema validation, hashing, non-destructive conversion on working copies, test execution, and bounded analysis that emits a declared artifact.

## Do not use it as the sole control when

- the worker needs unconstrained planning or must decide the mission;
- outputs cannot be mechanically asserted;
- the operation is irreversible or directly mutates bare metal;
- operating-system isolation, privilege dropping, resource ceilings, network confinement, or independent durability is required but absent;
- the source generation or target identity is ambiguous;
- the contract would need to be altered during the run;
- a prior attempt may still be active and ownership cannot be proven.

## Preflight

1. Obtain the engine independently and verify its SHA-256 against `SOURCE_RECEIPTS.json`.
2. Extract only after rejecting absolute paths, parent traversal, and links.
3. Run the vendor tests in a disposable working directory.
4. Create a new contract from the vendor template; never edit the preserved source template in place.
5. Bind the contract to the Mission Capsule, actor, authority, source generation, idempotency, input digests, output assertions, finite budgets, and allowed recovery actions.
6. Review every command argv and inherited environment name. Shell execution is forbidden by engine v0.2, but an allowed executable can still perform broad effects.
7. Confirm the working directory and output paths are copies or new child targets.

## State translation

| Engine state | Prompt-workflow state | Required response |
|---|---|---|
| Contract rejected | `PROBLEM / CONTRACT` | Correct only through a new reviewed contract |
| Running | `OFFLOADING STATE: active` | Keep the Mission Capsule resident; do not infer progress |
| Recovery selected | `OFFLOADING STATE: active-recovery` | Verify action was predeclared and budgeted |
| `FINISHED` | `finished-candidate` | Verify receipt and egress; do not declare user-task completion |
| `PROBLEM` | `quarantined` | Preserve evidence and enter degraded continuity |
| Engine missing/interrupted | `unavailable` | Use the resident no-offload fallback |
| Journal/contract integrity failure | `quarantined` | No autonomous repair or inferred resume |

## Fallback relationship

The engine's internal ladder handles declared workload faults: SAFE → FALLBACK → RECOVERY → RESTART → RECOVER → REBUILD → QUARANTINE/ESCALATE. The prompt kit's resident degraded mode handles failure of the offloading capability itself. These layers must not call each other recursively.

If the engine exhausts its authority or cannot prove a terminal state, the outer workflow stops or contracts to one reversible resident step. It does not create another supervisor, widen permissions, or repeat the job outside the contract.

## Evidence returned to the LLM

The conversational layer should receive only a bounded terminal packet by default:

```text
ENGINE TERMINAL STATUS: FINISHED / PROBLEM
CONTRACT DIGEST:
OPERATION ID:
OBJECT ID:
SOURCE GENERATION:
PRIMARY ATTEMPTS:
RECOVERY ACTIONS:
RECEIPT PATH OR POINTER:
RECEIPT SHA-256:
PROBLEM KIND / REASON:
```

Detailed journals remain available for verification or postmortem. Their existence does not make local evidence independently durable.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
