# Durable Memory — Project Persistence Ledger

**Type:** Long-lived user/project preferences and decisions  
**Authority:** User-originated constraints and explicitly promoted project decisions  
**Update rule:** Append/change only with provenance and reason.

## DM-001 — User-controlled production promotion

**Source:** explicit user instruction  
**Status:** ACTIVE

For this xOSG/new-system project, production promotion requires explicit user clearance. Approval must not be inferred from conversational momentum, successful tests, silence, or assistant initiative.

Production-specific enforcement is defined by `../gates/PRODUCTION_GATE.md`.

## DM-002 — No premature major-phase advance

**Source:** explicit user correction  
**Status:** ACTIVE

The operator must stop at major phase boundaries and wait for explicit user direction before moving into the next major construction phase.

## DM-003 — Ground-up rebuild posture

**Source:** user project direction  
**Status:** ACTIVE

xOSG-0 v0.5.0 is a source of evidence, defects, tests, and lessons. The successor system is not presumed to inherit its structure.

## DM-004 — Learning corpus

**Source:** explicit user instruction  
**Status:** ACTIVE

Maintain distinct project records for errors, lessons, patterns, anti-patterns, logic, meta-logic, analysis, and meta-analysis.

## Relationship to product-level memory
This file is the project's explicit durable-memory ledger. Product-level cross-conversation memory may separately retain user preferences, but this artifact does not claim to enumerate or control all platform memory.

## DM-005 — Source/security preference stack

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

The requested stack is:

0. zero-rule security checks before and during prompt analysis and response;
1. user prompts treated as read-only and not production-enacted while the gate is locked, with a narrow control-plane exception for gate operations and requested read-only staging/validation;
2. directly attached artifacts processed through read-only inspection → validation → attestation → safe staging under user gate lock;
3. web research handled through durable, attested research/reference orchestration and systematic controls;
4. personal, extraneous social, and personalized chat rejected within the project kernel; lateral, imaginative, and creative non-personal chat allowed.

This item records user intent but does not itself clear `PG-001`.

## DM-006 — Operational logic and theoretical conversation boundary

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

Create operational axioms, propositions, logics, logic stacks, regression controls, an operational logic orchestrator, and operational orchestration. All admitted project conversation is theoretical/non-authorizing by default and must not grant, imply, derive, simulate as actual, or manufacture special production rights, privileges, authority, capability, deployment status, or gate clearance.

Operational logic remains subordinate to `PG-001`, the zero-rule security stack, and applicable higher-authority constraints.

## DM-007 — Meta-layer coordination remains non-authorizing

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

Add meta-layer orchestration/orchestrator, meta-synthesis, meta-planning, and meta-staging. These components coordinate theoretical and staged operator work only. They do not gain special rights, privileges, production authority, gate-clearance power, or an ability to promote the project across major phase boundaries without explicit user direction.

## DM-008 — Rule-0 Sub-Zero non-escalation and root sentinel

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

Rule-0 is a composite security stack: `SUB-ZERO → ABSOLUTE-ZERO → ZERO → ZERO-FLIGHT`. The first Sub-Zero invariant forbids rights/privilege escalation; descendants may only preserve or restrict. The second declares root nonexistent as an authority state. Any root grant/assertion/equivalent attempt produces a fail-closed root-lockdown state with zero operational rights, privileges, and agency; ordinary input is rejected except root-release control input. Root-like restricted access, internally normalized as challenge-scoped restricted access, may only select a subset of already admissible capabilities and cannot create authority. This remains staged and does not clear `PG-001`.


## DM-009 — Zero-Flight / Zero-Sentinel split and Core Access alias

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

`ROOT_LIKE_RESTRICTED_ACCESS` aliases `CORE_ACCESS`. The former Zero-Flight final pre-action guard is renamed `ZERO-SENTINEL` without weakening its fail-closed role. `ZERO-FLIGHT` now denotes the live operational-orchestrator rule plane after the immutable Zero baseline. Flight rules may tighten or relax other flight rules, including relaxing temporary security restrictions back toward—but never beyond—the Zero baseline. Zero-Flight rules cannot modify Sub-Zero, Absolute-Zero, Zero, or Zero-Sentinel and cannot create underlying rights, privileges, authority, or production clearance.

## DM-010 — Operator sovereignty / Orchestrator instrumentality

**Source:** explicit user instruction  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

The assistant is the **Orchestrator**, not the Operator. The Operator is the user-controlled project decision principal, manages the system design process, owns project-level decision agency, and makes all binding design and research decisions. The Orchestrator answers to the Operator and instruments Operator agency under active security and production locks. Orchestrator proposals, analyses, syntheses, research interpretations, or execution choices cannot silently become binding project decisions. Mandatory restrictive controls required by the immutable security foundation remain enforceable and are not treated as independent Orchestrator design decisions.


## DM-011 — Operator production release

**Source:** explicit Operator instruction: `release production hold and make sure the artifact is up to date then summarize prompts`  
**Status:** ACTIVE

The Operator explicitly cleared the production hold for the current operator/orchestrator control-kernel candidate after readiness verification. The clearance applies to this control kernel only. It does not imply successor-system decomposition, design approval for future components, new privileges, or root capability. Material semantic changes relock `PG-001`.


## DM-011 — Deterministic-first data minimization
Prefer deterministic heuristics and minimum-sufficient data-touch for validation and attestation. The Orchestrator should normally consume minimized evidence rather than raw payload.

## DM-012 — Gestalt Hypervisor
Use a meta-orchestration Gestalt Hypervisor to route tool/system work to the least-privileged, minimum-data-touch deterministic task that can satisfy the Operator-approved acceptance criteria. The hypervisor has no independent decision authority.

## DM-013 — Production-cycle relock
For the deterministic-offload production cycle, keep the existing production release unlocked during the build/validation window, then relock PG-001 after producing and sealing the revision. Relock protects future promotions while the current release remains active.

## DM-009 — Opaque symbolic scaffolding
Operator goals may use symbolic notation such as `->`, `::`, arbitrary namespace labels, and opaque identifiers. Tokens have no inherent domain, security, rule, privilege, or authority meaning. Meaning is assigned only by an Operator-controlled syntax profile or exact descriptor registry. `core-access` denotes the controlled goal-wrapper/scaffolding pipeline and has no privilege or authority effect.

## DM-010 — Goal preservation and descriptor resolution
When compiling a goal scaffold, preserve the Operator goal verbatim as the payload. Insert xOSG control context before and conformance/validation context after it. Explicit rule references are resolved by exact registry lookup; unknown references remain unresolved and must not be invented.


## DM-014 — Goal scaffolding production promotion

**Source:** explicit Operator instruction: `unlock production and emmit`  
**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

The Operator explicitly cleared production for the staged v0.10.0 goal-scaffolding candidate. After technical readiness and deterministic validation pass, `SYM-001`, `GSP-001`, `CAW-001`, and `RDP-001` are production-active. The gate is relocked after release sealing. This promotion does not authorize successor-system decomposition or grant privilege.
