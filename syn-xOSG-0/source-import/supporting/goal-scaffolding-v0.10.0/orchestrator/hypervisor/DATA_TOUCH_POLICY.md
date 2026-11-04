# Data-Touch Minimization Policy — DTM-001

## Objective

Minimize how much source data is semantically exposed to the Orchestrator during validation and attestation.

## Exposure classes

```text
DT0 = NO CONTENT        : task IDs, declared paths, control state only
DT1 = METADATA          : path, size, mode, timestamps when needed
DT2 = DIGEST            : streaming cryptographic hash / Merkle evidence
DT3 = STRUCTURE         : syntax/schema/shape without returning raw payload
DT4 = BOUNDED PROBE     : exact invariant probes or bounded excerpts
DT5 = FULL SEMANTIC     : full-content model inspection; last resort
```

Selection rule:

```text
choose MIN(DTn) such that task_acceptance_criteria can be decided deterministically
```

## Validation default

Validation defaults to `DT1..DT3`. `DT4` requires an explicit named invariant or failure investigation. `DT5` requires a reason recorded in the task evidence.

## Attestation default

Attestation consumes generated evidence, not original content, whenever possible:

```text
inventory -> hashes -> Merkle root -> regression results -> scoped attestation
```

## Model-exposure distinction

A deterministic program may stream bytes to calculate a digest without returning those bytes to the Orchestrator. This counts as mechanical data access but not semantic model exposure.

## Fail-closed rule

If a claim cannot be established at the permitted data-touch level:

```text
result = UNVERIFIED | HOLD
```

The system must not silently escalate to broader content exposure.
