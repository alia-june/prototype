<div align="center">

# Mill Factory

### Evidence-bearing work batches with fail-closed promotion

![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Runtime](https://img.shields.io/badge/runtime-PowerShell-5391FE)
![Method](https://img.shields.io/badge/method-evidence--first-2f81f7)
![Decision](https://img.shields.io/badge/default-HOLD-b23c17)

**A small PowerShell factory for turning experimental work into inspectable,
reproducible batches without confusing structure, validation, acceptance, and
runtime proof.**

</div>

---

## Why this exists

Experimental work often mixes source material, generated candidates, test
results, decisions, and release files in one directory. Mill Factory separates
those roles and makes every promotion step explicit.

Each batch begins as generated working evidence with every gate pending and the
decision fixed to `HOLD`.

```text
intake → source freeze → candidate → static → compiler → package → live
                                                                   │
                                                                   v
                                              hold / revise / reject / promote
```

A batch may be structurally valid while still being uncompiled, untested,
unaccepted, or unsuitable for production. The ledgers preserve that distinction.

## Features

- Dated, non-overwriting batch creation.
- Safe ZIP inventory and expansion without executing archive contents.
- Deterministic SHA-256 manifests.
- Separate source, candidate, static, compiler, package, live, and decision
  evidence directories.
- Append-only gate and decision ledgers.
- Typed sentinel, reference, and glue contracts.
- Evidence-required `PASS`, `FAIL`, and `BLOCKED` gate results.
- Promotion only after all gates pass and explicit approval evidence exists.
- Immutable promoted batches.
- Positive and negative controls for tamper detection and promotion logic.

## Quick start

Requirements: PowerShell 7 or newer.

From this project directory, create a batch:

```powershell
& .\New-MillBatch.ps1 `
  -Slug 'reference-adapter-v1' `
  -Title 'Reference Adapter V1' `
  -Scope 'Bounded adapter candidate with structural and live validation.'
```

By default the batch is created beneath `./mill/` in the caller's working
directory. Use `-OutputRoot` for an explicit location.

The command refuses to overwrite an existing batch with the same slug and date.

## Import supplied source

Import and safely expand a ZIP as source evidence:

```powershell
& .\Import-MillSourceArchive.ps1 `
  -BatchPath .\mill\reference-adapter-v1-2026-11-04 `
  -ArchivePath C:\path\to\source.zip `
  -SourceId 'source-package-001' `
  -Relevance 'Supplied implementation and design source.' `
  -Expand
```

The importer inventories paths, refuses unsafe or duplicate entries, records
the archive digest, copies the original, and optionally expands it. It does not
execute imported files.

## Validate and seal

Validate structure, ledgers, contracts, decision logic, and manifest identity:

```powershell
& .\Test-MillBatch.ps1 `
  -BatchPath .\mill\reference-adapter-v1-2026-11-04
```

Refresh the manifest only after an intentional change:

```powershell
& .\Update-MillManifest.ps1 `
  -BatchPath .\mill\reference-adapter-v1-2026-11-04 `
  -Write
```

An unexplained file change causes validation to fail until it is reviewed and
resealed.

## Record a gate

Non-pending gate states require an evidence file inside the batch:

```powershell
& .\Set-MillGate.ps1 `
  -BatchPath .\mill\reference-adapter-v1-2026-11-04 `
  -Gate static `
  -Result PASS `
  -EvidencePath evidence/static/VALIDATION_RESULTS.json `
  -Reviewer 'local-validator'
```

Available gates:

```text
source_freeze
candidate
static
compiler
package
live
```

Gate results are `PENDING`, `PASS`, `FAIL`, or `BLOCKED`.

## Promotion

Promotion is fail-closed. It requires:

1. all six gates equal `PASS`;
2. a named authorizer;
3. an approval-evidence file inside the batch.

```powershell
& .\Set-MillDecision.ps1 `
  -BatchPath .\mill\reference-adapter-v1-2026-11-04 `
  -Decision PROMOTE `
  -AuthorizedBy 'explicit-reviewer' `
  -ApprovalEvidencePath evidence/decision/APPROVAL.md
```

Once promoted, the batch becomes immutable. Further work belongs in a new
batch rather than a silent mutation of the accepted record.

## Sentinel, reference, and glue contracts

The factory distinguishes three cross-cutting concerns:

| Contract | Governing question |
|---|---|
| Sentinel | What does absence, ambiguity, danger, or terminal state mean? |
| Reference | Which continuing object or version-pinned snapshot is intended? |
| Glue | How may data cross between declared producer and consumer contracts? |

A passing glue edge must consume resolved references and carry evidence. Glue
may translate representation; it may not invent semantics, erase a sentinel,
silently widen authority, or own an undeclared recovery loop.

These checks are structural. They do not establish semantic equivalence between
producer and consumer.

## Batch layout

```text
mill/<slug>-<date>/
├── source/                     supplied and frozen source material
├── candidate/                  generated implementation or design candidate
├── harness/                    bounded validation harnesses
├── package/                    delivery candidate
├── audit/                      inspection records
├── rollback/                   recovery artifacts
├── evidence/
│   ├── source/
│   ├── candidate/
│   ├── static/
│   ├── compiler/
│   ├── package/
│   ├── live/
│   └── decision/
├── MILL_BATCH.json             current truth, gate, and decision state
├── SOURCE_INVENTORY.csv
├── CLAIM_LEDGER.csv
├── GATE_LEDGER.csv
├── DECISION_LEDGER.csv
├── VALIDATION_PLAN.csv
├── LIVE_RESULTS.csv
├── SENTINEL_REGISTRY.json
├── REFERENCE_REGISTRY.json
├── GLUE_LEDGER.csv
└── MANIFEST.sha256
```

## Project layout

```text
mill-factory/
├── New-MillBatch.ps1
├── Import-MillSourceArchive.ps1
├── Test-MillBatch.ps1
├── Update-MillManifest.ps1
├── Set-MillGate.ps1
├── Set-MillDecision.ps1
├── templates/
└── tests/
    └── Test-MillFactory.ps1
```

## Replay the controls

```powershell
& .\tests\Test-MillFactory.ps1
```

The disposable suite exercises creation, portable default output, unresolved
glue refusal, duplicate refusal, tamper detection, intentional resealing,
premature-promotion refusal, fully gated promotion, and post-promotion
immutability.

## Validation boundary

A factory `PASS` establishes only the implemented structure and internal
consistency checks. It does not prove:

- source truth or semantic correctness;
- successful compilation;
- runtime behavior or visual quality;
- package fitness or legal clearance;
- acceptance as project canon;
- authorization beyond the recorded decision scope.

Each gate's evidence must support its own claim. Missing evidence remains
`PENDING`, `UNKNOWN`, or `BLOCKED` rather than becoming an implicit pass.

## Status

**Prototype / generated implementation candidate.**

See [VALIDATION.md](VALIDATION.md) for the repository replay and
[PROVENANCE.md](PROVENANCE.md) for the adaptation boundary.

No license file is currently included. Do not assume redistribution or reuse
rights until the repository owner selects and adds a license.

<div align="center">

---

**Make the state visible. Keep the evidence attached. Promote only what was
actually reviewed.**

</div>
