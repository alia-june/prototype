# Durable Research Orchestration — DRO-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL  
**Production gate:** `PG-001` CLEARED_FOR_CURRENT_RELEASE

## Purpose

Turn web research into a reproducible evidence process rather than a transient search result stream.

## Research record

Each material research task SHOULD record:

- research question;
- scope and exclusions;
- search/retrieval date;
- source identity and source type;
- publication/update date when available;
- claim(s) supported;
- contradictory sources;
- confidence/uncertainty notes;
- whether the finding is source-derived, derived, inferred, or proposed;
- citation/reference pointer;
- validation/cross-check performed;
- durable disposition: retained, superseded, rejected, unresolved.

## Source preference

Prefer, where appropriate:

1. authoritative primary sources;
2. high-quality current secondary sources;
3. specialist or technical references;
4. community/experiential sources for sentiment or lived experience, clearly typed as such.

Source priority is contextual, not absolute. A primary source may establish what an organization says; it does not automatically establish every disputed factual conclusion about itself.

## Systematic control

```text
QUESTION
→ SEARCH PLAN
→ RETRIEVE
→ CLASSIFY
→ EXTRACT CLAIMS
→ LINK CLAIMS TO SOURCES
→ CROSS-CHECK MATERIAL CLAIMS
→ RECORD DISAGREEMENT
→ ATTEST RESEARCH PASS
→ STAGE RESULT
```

## Durable reference building

Material references are intended to survive the individual response. A future implementation may serialize them into a reference ledger/database. Until then, the project artifact must preserve enough metadata to reconstruct provenance.

## Gate boundary

Research can inform a staged proposal while `PG-001` is locked. Research cannot itself clear the gate or authorize production enactment.

## Operator research authority — SZR-003

Binding research decisions belong to the Operator. The Orchestrator instruments those decisions.

Operator-controlled research decisions include:

- research objective/question;
- material scope and exclusions;
- admissibility/source policy;
- acceptance criteria;
- whether a material ambiguity is resolved, left unresolved, or requires more research;
- whether research findings alter a design decision.

The Orchestrator may derive and execute mechanical search syntax, retrieval ordering, deduplication, extraction, citation linking, and cross-check steps inside an already authorized research scope. If a mechanical choice would materially change scope, admissibility, conclusion criteria, or design consequence, it becomes a `RESEARCH_DECISION_CANDIDATE` and returns to the Operator.

```text
RESEARCH_DECISION_SOURCE = OPERATOR
RESEARCH_INSTRUMENTATION = ORCHESTRATOR
```
