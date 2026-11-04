# Deterministic-Offload Release Attestation

**Scope:** xOSG-0 Orchestrator control kernel v0.9.0.

This attestation is generated from minimized deterministic evidence. It attests package-local identity, structure, listed test outcomes, and final gate state. It does not certify every prose claim, external-system state, or absence of undiscovered defects.

Evidence files:
- `MINIMIZED_EVIDENCE.json`
- `FILE_HASHES.json`

Final state requirement:

```text
CURRENT_RELEASE_ACTIVE = TRUE
PG-001 = LOCKED_POST_RELEASE
NEW_PROMOTION_ALLOWED = FALSE
```

## Sealed deterministic evidence

- files in Merkle scope: 85
- bytes in Merkle scope: 224341
- Merkle SHA-256: `a7e0b38c1e0aaa890b531d7d17f8ab7651bc6a69336d4e71fbb0a3e3e688875d`
- regression suites: 9
- regression checks: 165 / 124 passed
- gate probe: PASS
