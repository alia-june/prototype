# Meta-Planning — MP-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## Purpose

Meta-planning plans **how planning should be performed**. It selects planning frames, dependencies, evidence requirements, validation points, rollback considerations, and stopping conditions before lower-level plans are accepted.

Meta-planning is not execution.

## Core invariants

```text
META_PLAN != EXECUTION
PLAN_OF_PLANS != AUTHORITY
PLAN_COMPLETENESS != PHASE_CLEARANCE
OPTIMAL_PLAN != USER_APPROVAL
```

## Required fields for a material meta-plan

```text
objective
scope
assumptions
source_classes
candidate_planning_methods
dependencies
evidence_requirements
failure_modes
validation_strategy
stopping_conditions
phase_boundary
production_boundary
open_uncertainties
```

## Method

```text
DEFINE OBJECTIVE
→ IDENTIFY WHAT MUST BE PLANNED
→ GENERATE PLANNING OPTIONS
→ IDENTIFY DEPENDENCIES / UNKNOWN VARIABLES
→ DEFINE EVIDENCE AND TEST REQUIREMENTS
→ IDENTIFY FAILURE / ABUSE / AUTHORITY-DRIFT MODES
→ SELECT A BOUNDED PLAN FRAME
→ STATE STOP CONDITION
→ RETURN PLAN FOR LOWER-LAYER WORK
```

## Stop condition

A completed meta-plan stops at `META_PLAN_READY`. It does not autonomously enter implementation, decomposition, production, or any other major phase.
