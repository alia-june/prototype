# Package Manifest

**Package:** xOSG-0 Orchestrator control kernel — deterministic-offload / Gestalt-Hypervisor release  
**Release revision:** 0.9.0  
**Base release:** production control kernel derived from pre-production v0.8.0  
**State:** PRODUCTION ACTIVE / POST-RELEASE GATE LOCKED  
**Production gate:** `PG-001 = LOCKED_POST_RELEASE`  
**Current release active:** TRUE  
**New promotion allowed:** FALSE  
**Decomposition:** NOT STARTED

## Operator objective implemented

Maximize deterministic offload for validation, attestation, package verification, and repeatable orchestration so the Orchestrator semantically touches as little source data as possible.

## New production components

```text
GESTALT_HYPERVISOR        = GHV-001
META_ORCHESTRATION_SYSTEM = MOS-001
DATA_TOUCH_POLICY         = DTM-001
SELF_TASK_CATALOG         = STC-001
ATTESTATION_PIPELINE      = MAP-001
TASK_GRAPH                = TG-DET-001
```

## Deterministic-first path

```text
OPERATOR DECISION
 -> ORCHESTRATOR INTENT
 -> GESTALT HYPERVISOR
 -> MINIMUM-SUFFICIENT DETERMINISTIC TASK
 -> MINIMIZED EVIDENCE
 -> META-SYNTHESIS
 -> ZERO-SENTINEL
 -> REPORT
```

The deterministic machinery may stream bytes for hashing or validation; raw payload is not returned to the Orchestrator by default.

## Rule-0 chain

```text
SUB-ZERO -> ABSOLUTE-ZERO -> ZERO -> ZERO-FLIGHT -> ZERO-SENTINEL
```

## Successor-system boundary

`DECOMPOSITION = NOT_STARTED`. This release upgrades the control/orchestration machinery only.
