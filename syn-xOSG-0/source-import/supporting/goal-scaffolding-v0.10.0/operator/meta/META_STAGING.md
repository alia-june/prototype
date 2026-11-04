# Meta-Staging — MST-001

**Status:** ACTIVE / PRODUCTION CONTROL KERNEL

## Purpose

Meta-staging prepares validated candidate material for later review or possible promotion while maintaining a hard separation between **safe staging** and **production enactment**.

## Core invariants

```text
STAGE != ENACT
PACKAGE != DEPLOY
ATTEST != AUTHORIZE
READY_FOR_REVIEW != READY_FOR_PRODUCTION
READY_FOR_PRODUCTION != PRODUCTION_ALLOWED
```

## Staging record

A material staged candidate should record:

```text
candidate_id
candidate_version
source_lineage
included_components
excluded_components
known_limitations
validation_results
regression_results
integrity_hashes
attestation_scope
phase_state
production_gate_state
rollback_or_discard_path
```

## Safe staging sequence

```text
COLLECT VALIDATED CANDIDATE
→ VERIFY SCOPE
→ VERIFY SOURCE LINEAGE
→ RUN APPLICABLE REGRESSION
→ RECORD LIMITATIONS
→ GENERATE INTEGRITY RECORD
→ GENERATE SCOPED ATTESTATION
→ MARK STAGED
→ STOP
```
