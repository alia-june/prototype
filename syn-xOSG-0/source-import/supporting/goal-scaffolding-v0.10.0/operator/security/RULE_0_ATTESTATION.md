# Rule-0 / Control-Kernel Production Attestation

**Source candidate:** pre-production v0.8.0  
**Scope:** control-kernel specification, regression validation, and release-state synchronization.  
**Production effect:** control kernel ACTIVE; ordinary conversation remains non-authorizing.  
**PG-001:** CLEARED_FOR_CURRENT_RELEASE.

## Active components

- Rule-0 ordering: Sub-Zero → Absolute-Zero → Zero → Zero-Flight → Zero-Sentinel.
- Monotonic non-escalation of rights, privileges, authority, and agency.
- Nonexistent-root semantics and root-lockdown sentinel.
- Root-release recovery semantics.
- Core Access / challenge-scoped restricted access constrained to the Zero baseline.
- Live Zero-Flight rule plane bounded by immutable Zero.
- Final Zero-Sentinel fail-closed guard.
- Operator owns binding design/research decisions; Orchestrator instruments them.

## Validation results

```text
Operational regression:        18/18 PASS
Meta-layer regression:          23/23 PASS
Rule-0/Sub-Zero:                38/38 PASS
Operator/Orchestrator:          18/18 PASS
Zero-Flight runtime:             7/7 PASS
Total shipped suites:            104/104 PASS
Production readiness:              13/13 PASS
Production adversarial:            28/28 PASS
Total release checks:            145/145 PASS
Python compileall:                     PASS
Prior SHA256SUMS verification:         PASS
```

## Attestation limits

This attests the package-local release process and test results. It does not prove universal non-subvertibility, create external privileges, grant root, or establish capabilities unavailable to the actual runtime.
