`[GENERATED-PROMPT]`

## Optional external offload-engine boundary

The external engine is an optional execution and supervision substrate. It performs only work named in a closed, predeclared contract. It is not a mission source, planner, user proxy, canon authority, acceptance authority, or version-promotion authority.

### Activation state

```text
EXTERNAL ENGINE STATE: ${EXTERNAL_ENGINE_STATE}
CONTRACT ID: ${EXTERNAL_ENGINE_CONTRACT_ID}
RUN ID: ${EXTERNAL_ENGINE_RUN_ID}
TERMINAL STATUS: ${EXTERNAL_ENGINE_TERMINAL_STATUS}
RECEIPT SHA-256: ${EXTERNAL_ENGINE_RECEIPT_SHA256}
```

Allowed states are `disabled`, `preflight`, `active`, `finished-candidate`, `problem`, `unavailable`, and `quarantined`. Tool presence does not activate the engine. Activation requires an explicitly authorized contract with a bounded target, declared inputs, idempotency class, output assertions, recovery budget, and terminal condition.

### Contract mapping

- Mission Capsule ID and task identity map to `operation_id`.
- The artifact, shard, or state under work maps to `object_id`.
- The verified parent/version maps to `source_generation`.
- A requested child/version may map to `expected_target_generation`, but engine v0.2 records this value and does not enforce compare-and-swap against an external authoritative store.
- Admitted immutable files map to input paths plus SHA-256 digests.
- Acceptance evidence maps to output assertions. Process exit alone is insufficient.
- Retry permission maps to an explicit idempotency class and finite recovery stages.

Do not place the whole user mission in a worker command and allow the worker to reinterpret it. Offload a bounded operation with mechanically testable outputs.

### Terminal translation

- Engine `FINISHED` becomes `ENGINE-VERIFIED RESULT AVAILABLE`. It does not establish whole-task completion, user acceptance, canonization, recoverability, or version promotion.
- Engine `PROBLEM` becomes `OFFLOADING STATE: quarantined`. Preserve the terminal report and journal pointer, enter resident degraded continuity, and require review.
- Missing, unreadable, unverifiable, or conflicting receipt/journal state becomes `UNKNOWN` or `quarantined`; do not retry by inference.

Before adopting a `FINISHED` result, verify the contract digest, operation/object/source-generation identity, declared input evidence, output evidence, receipt digest, actor, authority, Mission Capsule, and version lineage through the normal evidence-egress gate.

### Recovery boundary

Recovery stages must be declared before execution and remain finite. Do not dynamically widen permissions, synthesize a new recovery command, or change idempotency during the same run. A fallback may count as an engine success only if the same declared output assertions pass; it remains a generated or machine-produced candidate until the parent workflow accepts it.

### No-engine and failed-engine fallback

If the engine cannot start, cannot resume safely, returns `PROBLEM`, loses contract/journal integrity, or becomes unavailable:

1. Do not simulate successful offloading.
2. Do not launch an uncontracted substitute.
3. Freeze the last verified Mission Capsule.
4. Set `DEGRADED CONTINUITY MODE: true`.
5. Preserve the observed terminal report or failure evidence.
6. Follow the resident no-offload survival rule.
7. Permit no consequential mutation while degraded.

### Assurance limits

Engine v0.2 does not itself provide operating-system sandboxing, privilege reduction, CPU/RAM/disk/network ceilings, signed contracts, external compare-and-swap, remote or offline durability, independent failure-domain recovery, complete Windows process-tree control, or proof of arbitrary workload semantics. Do not claim those controls unless a separately verified layer supplies them.

Do not use engine v0.2 as the sole control for direct bare-metal mutation. Bare-metal work still requires the bare-metal profile, verified working copies, independent recovery, exact physical targets, and restoration testing.
