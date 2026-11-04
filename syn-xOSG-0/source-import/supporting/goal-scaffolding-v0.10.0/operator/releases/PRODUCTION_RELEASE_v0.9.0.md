# Production Release Record — v0.9.0

**Release:** deterministic-offload / Gestalt-Hypervisor control-kernel revision  
**Operator instruction:** keep production unlocked during production and relock after producing  
**Current release:** `PRODUCTION_ACTIVE`  
**Final gate:** `PG-001 = LOCKED_POST_RELEASE`  
**Successor-system decomposition:** NOT STARTED

## Scope

This release adds deterministic task composition, minimal-data-touch validation/attestation, a tool-governance Gestalt Hypervisor, and a meta-orchestration system. It does not modify the underlying model, platform tool privileges, or the immutable Rule-0 authority ceiling.

## Release-state distinction

```text
CURRENT_RELEASE_ACTIVE = TRUE
NEW_PROMOTION_ALLOWED  = FALSE
```

Relocking PG-001 after sealing protects future changes without deactivating this release.

## Evidence model

Release evidence is intentionally minimized:

- canonical inventory and sizes;
- SHA-256 file digests;
- deterministic Merkle root;
- regression result summaries;
- JSON/schema/structure validation results;
- bounded gate-state probe;
- archive integrity and external SHA-256.

Raw content is not part of the default attestation output.

## Attestation boundary

The evidence establishes package identity and recorded deterministic checks. It does not certify every prose statement as true, guarantee absence of undiscovered defects, or attest external systems.
