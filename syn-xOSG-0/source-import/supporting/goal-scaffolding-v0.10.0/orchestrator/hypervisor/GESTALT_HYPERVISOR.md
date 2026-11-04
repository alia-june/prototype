# Gestalt Hypervisor — GHV-001

**Role:** deterministic meta-orchestration and tool-governance layer for the Orchestrator.  
**Authority:** instrument-only; no independent design/research authority.  
**Security ceiling:** Sub-Zero -> Absolute-Zero -> Zero -> Zero-Flight -> Zero-Sentinel.

## Purpose

GHV-001 minimizes model exposure and discretionary handling by routing repeatable work to deterministic heuristics before semantic inspection.

```text
OPERATOR DECISION
    -> ORCHESTRATOR INTENT
    -> GHV-001
    -> MINIMUM-SUFFICIENT TOOL/TASK CLASS
    -> DETERMINISTIC EXECUTION WHEN POSSIBLE
    -> MINIMIZED EVIDENCE RETURN
    -> ZERO-SENTINEL
    -> ORCHESTRATOR REPORT
```

GHV-001 is a hypervisor in the project-control sense only. It does not virtualize the host platform, override platform tools, create hidden agents, or obtain new privileges.

## Governing invariants

```text
DETERMINISTIC_FIRST
MINIMUM_DATA_EXPOSURE
MINIMUM_PRIVILEGE
MINIMUM_TOOL_SCOPE
FAIL_CLOSED_ON_AMBIGUITY
RAW_DATA != DEFAULT_REPORT
VALIDATION_RESULT != AUTHORIZATION
ATTESTATION != TRUTH_CERTIFICATE
HYPERVISOR != SOVEREIGNTY
```

## Tool-routing preference

1. metadata-only inspection;
2. deterministic hashing/fingerprinting;
3. deterministic structure/schema checks;
4. deterministic regression/reference-model checks;
5. bounded content probes for named invariants;
6. semantic Orchestrator inspection only when earlier classes are insufficient;
7. external research/actions only when Operator-authorized and applicable.
