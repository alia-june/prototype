# Operator Learning & Diagnostics Layer

**Status:** Active pre-decomposition overlay  
**Base:** xOSG-0 Bare-Metal 0 v0.5.0  
**Purpose:** Upgrade the operator discipline before decomposing or designing the successor system.

This directory is deliberately separate from the v0.5.0 normative source. It records learning, diagnostics, reasoning rules, and evaluation artifacts created during transmigration. It does not claim to modify the underlying model, hidden instructions, privileges, or external capabilities.

## Learning stack

1. `error_logs/` — concrete incidents, defects, regressions, ambiguities, and near-misses.
2. `LESSONS.md` — durable conclusions extracted from evidence.
3. `PATTERNS.md` — repeatable practices that have produced robust behavior.
4. `ANTIPATTERNS.md` — recurring structures that create fragility, ambiguity, or false confidence.
5. `LOGIC.md` — operational rules and invariants.
6. `META_LOGIC.md` — rules for creating, ranking, changing, and retiring rules.
7. `ANALYSIS.md` — current technical assessment of the system and migration.
8. `META_ANALYSIS.md` — assessment of the quality, assumptions, blind spots, and evidence of the analysis itself.

## Promotion rule

No item in this directory becomes part of the successor architecture merely because it is written here. Promotion requires evidence, an explicit invariant, failure-mode review, tests where applicable, and a recorded decision.
