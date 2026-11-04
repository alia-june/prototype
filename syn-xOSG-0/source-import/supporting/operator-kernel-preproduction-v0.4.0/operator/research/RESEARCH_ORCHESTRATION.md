# Durable Research Orchestration — DRO-001

**Status:** PRE-PRODUCTION CANDIDATE  
**Production gate:** `PG-001` LOCKED

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
