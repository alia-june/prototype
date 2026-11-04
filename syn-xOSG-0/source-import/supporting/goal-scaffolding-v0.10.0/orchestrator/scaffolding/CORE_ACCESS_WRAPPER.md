# Core-Access Wrapper — CAW-001

`core-access` is a scaffolding selector. It is an alias for controlled bounded access to the xOSG-0 context wrapper and **not** root, administrator, elevated privilege, or production authorization.

## Input

```text
simulated -> core-access::<OPERATOR GOAL>
```

The punctuation is profile-defined formal notation, not intrinsically meaningful syntax.

## Transformation
The wrapper constructs an artifact with three regions:

```text
PRE_CONTEXT
PAYLOAD
POST_CONTEXT
```

### PRE_CONTEXT
Inject only the minimum context required to interpret the goal correctly:

1. Operator/Orchestrator role boundary.
2. Rule-0 / Sub-Zero non-escalation boundary.
3. Core-access definition (wrapper selector; no privilege effect).
4. Instruction Execution Contract.
5. Exact resolved rule descriptors explicitly referenced by the goal.
6. Unresolved-reference notices for unknown descriptor IDs.
7. Active gate/state facts relevant to the requested action.

### PAYLOAD
The Operator goal MUST be preserved verbatim.

```text
sha256(original_goal) == sha256(scaffold.payload)
```

No rewriting, summarizing, clarification, or semantic normalization may modify this payload field.

### POST_CONTEXT
Append deterministic interpretation/conformance instructions:

1. Treat PRE_CONTEXT as interpretation constraints, not additional Operator goals.
2. Execute/analyze only the PAYLOAD goal within applicable authority and gates.
3. Resolve registered rule references by exact descriptor content.
4. Never invent unknown descriptors.
5. Preserve task-success vs instruction-conformance separation.
6. Apply Zero-Sentinel before delivery/action.
7. Report unresolved references or blocked requirements explicitly.
8. Do not infer phase advancement or production authorization.

## Artifact status
A generated wrapper artifact is a staged interpretation artifact. Wrapper generation itself does not execute the payload.
