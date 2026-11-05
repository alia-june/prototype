> **FABRICATION FLAG — GENERATED TEXT BEGINS**

# Candidate 1.2 Engine Integration Audit

`[GENERATED-VERIFICATION-REPORT]`

## Accepted as useful evidence

The supplied engine implements a bounded local supervisor with closed JSON contracts, argv-only command execution, explicit idempotency classes, finite attempt/recovery budgets, deterministic recovery ordering, copied and hashed contracts, input-digest verification, output assertions, atomic state files, a hash-chained journal, single-supervisor leasing, terminal receipts, quarantine, and resume handling.

## Preserved distinctions

- Work execution is not mission authority.
- Process exit is not semantic completion.
- Engine `FINISHED` is not user acceptance or whole-task completion.
- A local hash chain is tamper-evident within its assurance boundary, not independent durability.
- A declared idempotency class is contract evidence, not proof.
- Recorded `expected_target_generation` is not externally enforced compare-and-swap in engine v0.2.
- Recovery of the workload is separate from fallback when the engine itself is unavailable.

## Integration result

Candidate 1.2 adds an optional `external_offload` profile and module. It maps Mission Capsule state into an engine contract, translates terminal states conservatively, requires the ordinary evidence-egress gate before adoption, and routes engine-level failure into the resident degraded-continuity fallback.

The engine archive is included unchanged. No engine source code was modified or promoted into the mandatory resident kernel.

## Residual limitations

The supplied v0.2 engine does not implement operating-system sandboxing, privilege reduction, CPU/RAM/disk/network ceilings, signed contracts, independent failure-domain storage, external target-generation enforcement, complete Windows process-tree termination, or arbitrary semantic validation. Candidate 1.2 therefore prohibits treating it as the sole control for direct bare-metal mutation.

> **FABRICATION FLAG — GENERATED TEXT ENDS**
