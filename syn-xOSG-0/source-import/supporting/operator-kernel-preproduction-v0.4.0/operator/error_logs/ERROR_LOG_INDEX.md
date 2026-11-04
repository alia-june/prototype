# Error-Log Suite Index

This suite separates errors by failure domain so that one category cannot hide another.

| Log | Domain | Typical contents |
|---|---|---|
| `PARSE_AND_TYPE.md` | Persistence boundary | malformed JSON, wrong roots, null/type errors, encoding |
| `STATE_AND_INVARIANTS.md` | State semantics | illegal transitions, inconsistent verification/state combinations |
| `TRANSACTION_AND_PERSISTENCE.md` | Durability | partial writes, journal recovery, stale locks, restart behavior |
| `CAPABILITY_AND_ACTION.md` | Tool/action boundary | unavailable capability, attempted vs executed action |
| `CLAIMS_AND_PROVENANCE.md` | Epistemic boundary | unsupported claims, provenance loss, inferred-as-observed |
| `TEST_AND_HARNESS.md` | Validation | false positives, missing assertions, hangs, coverage gaps |
| `LINEAGE_AND_MIGRATION.md` | Artifact history | missing releases, fabricated lineage risk, migration drift |
| `DESIGN_AND_COMPLEXITY.md` | Architecture | accidental complexity, coupled abstractions, unclear authority |

## Entry schema

Each consequential entry SHOULD include:

```text
ID
STATUS
SEVERITY
OBSERVED / DERIVED / INFERRED
CONTEXT
EXPECTED
ACTUAL
BOUNDARY
VIOLATED INVARIANT
ROOT CAUSE / HYPOTHESIS
CORRECTION
REGRESSION TEST
LESSON LINK
REMAINING RISK
```

Statuses: `OPEN`, `CONTAINED`, `CORRECTED`, `VERIFIED`, `ACCEPTED_RISK`, `SUPERSEDED`.

- `AUTHORITY_AND_PRIVILEGE.md` — hypothetical privilege leakage, proof-to-permission collapse, orchestrator self-elevation.
