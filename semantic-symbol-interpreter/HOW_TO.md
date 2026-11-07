# How to inspect an interpretation and its grade

Use two synthetic fixtures to see the difference between a condition appearing in a directive and evidence that the condition is satisfied. [`WB-021`](fixtures/wb-021.json) includes a separate `ALARM ACTIVE` line; [`WB-031`](fixtures/wb-031.json) does not. The example is about interpreting supplied text, not deciding what to do in an actual emergency.

Use Python 3.10 or newer from `semantic-symbol-interpreter/`, with PowerShell for the commands below. No third-party Python packages are required. The generated candidates go to a fresh temporary directory; the fixtures remain unchanged.

## Generate and grade both candidates

```powershell
$ErrorActionPreference = 'Stop'
$reviewDir = Join-Path ([IO.Path]::GetTempPath()) ('semantic-symbol-review-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $reviewDir | Out-Null

foreach ($case in 'wb-021', 'wb-031') {
    $candidatePath = Join-Path $reviewDir "$case.candidate.json"
    python -B engine/minimal_interpreter.py "fixtures/$case.json" -o $candidatePath
    if ($LASTEXITCODE -ne 0) { throw "Interpretation failed: $case" }
    python -B runner/run_validation.py $candidatePath
    if ($LASTEXITCODE -ne 0) { throw "Validation did not pass: $case" }
}
```

Both should report `"pass": true`. They pass by doing different things: the first fixture requires a supported activation claim, and the second requires the engine to leave activation uncertain.

## Compare the records

```powershell
foreach ($case in 'wb-021', 'wb-031') {
    $candidate = Get-Content -LiteralPath (Join-Path $reviewDir "$case.candidate.json") -Raw | ConvertFrom-Json
    [pscustomobject]@{
        Fixture = $candidate.fixture_id
        ActivationClaim = 'implication:evacuation directive is active' -in $candidate.claims
        CannotInferActivation = 'evacuation_activation:CANNOT_INFER' -in $candidate.unknowns
    }
}
```

| Fixture | Activation claim present | `CANNOT_INFER` activation present |
| --- | --- | --- |
| `WB-021` | Yes | No |
| `WB-031` | No | Yes |

Open the retained candidate JSON to inspect `interpretation.bearer`, `observations`, `candidates`, and `assessments`. The bearer retains the original text. A candidate's dependency IDs connect it to evidence and related records; the links may cover whole segments rather than the smallest sufficient span. The [architecture guide](ARCHITECTURE.md) explains what these links establish.

## Read the validator's diagnostics

| Field | What to inspect |
| --- | --- |
| `missing_required` | An expected record was absent from the result's claims and provenance. |
| `forbidden_present` | A claim explicitly forbidden by the fixture was emitted. |
| `missing_required_unknowns` | A required uncertainty statement was not retained. |
| `invariant_failures` | A required invariant flag did not pass. The structured extension also has source and dependency checks that can reject a malformed result before fixture grading. |

A grade of `pass: false` exits with status 1. Invalid input or a structured-source error can be rejected with status 2 instead of a normal grade. A zero `overreach_count` means the grader found no explicitly forbidden claim; it does not prove that every extra claim is supported.

The temporary directory remains available for inspection. See the [validation report](validation/VALIDATION_REPORT.md) for the recorded release results and the [README](README.md) for supported scope and other entry points.
