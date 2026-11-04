# System Memory — Effective Boundary Register

**Type:** Project-visible record of stable operating boundaries  
**Important limitation:** This file does not expose, reproduce, replace, or modify hidden system/developer instructions, private chain-of-thought, model weights, or platform internals.

## Purpose
Record the system-level constraints that the project must treat as externally authoritative without pretending the project controls them.

## SM-001 — Authority boundary
The project/operator layer cannot modify the underlying model, hidden platform instructions, privileges, or unavailable capabilities.

## SM-002 — Actual-action requirement
External actions, tool calls, file changes, connector operations, and other side effects count as executed only when they actually occurred through an available capability.

## SM-003 — Higher-authority constraints
Project rules, prompts, configuration, and production clearance remain subordinate to applicable platform safety, privacy, tool, and system constraints.

## SM-004 — Hidden reasoning boundary
The project may retain visible analysis artifacts, decisions, evidence, and summaries, but it does not log or expose private hidden chain-of-thought.

## SM-005 — Evidence boundary
Claims about runtime state, test results, artifacts, and external actions require evidence appropriate to the claim.

## SM-006 — Production gate scope
User clearance can authorize project production only within the capabilities and constraints actually available. It cannot grant unavailable privileges or override higher-authority restrictions.
