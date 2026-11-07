# How to use Mill Factory: a disposable batch

This walkthrough creates a batch, imports a ZIP containing one harmless text file, records why a gate is blocked, and records an explicit `HOLD`. It leaves a batch you can inspect. It does not promote a candidate or execute imported content.

Use **PowerShell 7 or newer**. Start in the `mill-factory/` directory. Run the blocks in order in the same session. All example writes go to a unique folder under the system temporary directory.

## 1. Create a batch and sample source

```powershell
$ErrorActionPreference = 'Stop'
$demoRoot = Join-Path ([IO.Path]::GetTempPath()) ('mill-how-to-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $demoRoot | Out-Null

$sample = Join-Path $demoRoot 'sample.txt'
$archive = Join-Path $demoRoot 'sample.zip'
Set-Content -LiteralPath $sample -Value 'Disposable Mill source example.' -Encoding utf8
Compress-Archive -LiteralPath $sample -DestinationPath $archive

$created = & ./New-MillBatch.ps1 -OutputRoot (Join-Path $demoRoot 'batches') `
    -Slug 'docs-walkthrough' -Title 'Disposable documentation walkthrough' `
    -Scope 'Inspect source intake and a held batch without promoting it.' |
    ConvertFrom-Json
$batch = $created.batch_path
$created | Format-List result, decision, batch_path
```

Expect `BATCH_CREATED` and `HOLD`. Use the returned path rather than guessing the date in the batch directory name.

## 2. Import the sample and inspect the structural result

```powershell
$intake = & ./Import-MillSourceArchive.ps1 -BatchPath $batch -ArchivePath $archive `
    -SourceId 'walkthrough-source' -Relevance 'Synthetic text for intake inspection.' -Expand |
    ConvertFrom-Json
$intake | Format-List result, archive_sha256, execution_status

$structure = & ./Test-MillBatch.ps1 -BatchPath $batch | ConvertFrom-Json
$structure | Format-List result, manifest_pass, evidence_boundary
```

Expect `SOURCE_IMPORTED` and `NOT_EXECUTED`, followed by a structural `PASS`. The source inventory identifies the input archive; the manifest checks retained bytes. This result does not pass any candidate gate. No candidate has been supplied.

## 3. Record a blocked gate and keep the batch on hold

```powershell
$evidencePath = 'evidence/candidate/WALKTHROUGH_BLOCKED.md'
Set-Content -LiteralPath (Join-Path $batch $evidencePath) -Encoding utf8 `
    -Value 'No candidate was supplied. Candidate evaluation cannot proceed.'

$gate = & ./Set-MillGate.ps1 -BatchPath $batch -Gate candidate -Result BLOCKED `
    -EvidencePath $evidencePath -Reviewer 'walkthrough-operator' | ConvertFrom-Json
$decision = & ./Set-MillDecision.ps1 -BatchPath $batch -Decision HOLD `
    -Notes 'Source intake only; no candidate or promotion requested.' | ConvertFrom-Json
$checked = & ./Test-MillBatch.ps1 -BatchPath $batch | ConvertFrom-Json

$state = Get-Content -LiteralPath (Join-Path $batch 'MILL_BATCH.json') -Raw | ConvertFrom-Json
[pscustomobject]@{
    CandidateGate = $state.gates.candidate
    Decision = $decision.decision
    Authorized = $decision.authorized
    StructuralCheck = $checked.result
    Batch = $batch
} | Format-List
```

Expect `CandidateGate = BLOCKED`, `Decision = HOLD`, `Authorized = False`, and `StructuralCheck = PASS`. The structural check can pass with a blocked gate because it checks the consistency of the batch records, not whether the work is ready to promote.

Inspect `SOURCE_INVENTORY.csv`, `GATE_LEDGER.csv`, `DECISION_LEDGER.csv`, and `MANIFEST.sha256` in the printed batch folder. The walkthrough leaves that temporary folder in place for review.

For real work, gather evidence appropriate to each gate. A structural `PASS` or a recorded `HOLD` cannot substitute for the six passing gates, named authorizer, and approval evidence required for `PROMOTE`. See [Architecture](ARCHITECTURE.md) for the boundaries and the [project README](README.md) for the full command and contract overview.
