# Lineage & Migration Error Log

## ERR-LM-001 — Missing historical release binaries

- **Status:** CONTAINED
- **Severity:** MEDIUM
- **Evidence class:** OBSERVED in prior consolidation
- **Actual:** narrative referenced intermediate releases that were not present in the available artifact inventory.
- **Invariant:** absent historical artifacts MUST NOT be reconstructed and presented as originals.
- **Control:** record discrepancy; preserve exact available artifacts; create a new consolidated build instead of fabricating lineage.

## ERR-LM-002 — Legacy feature inherits authority by age

- **Status:** ACTIVE CONTROL
- **Severity:** HIGH
- **Failure:** old behavior is retained simply because later components depend on it.
- **Control:** every inherited primitive must rejustify the problem it solves and survive ground-zero evaluation.
