[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath,
    [Parameter(Mandatory = $true)]
    [ValidateSet('source_freeze', 'candidate', 'static', 'compiler', 'package', 'live')]
    [string]$Gate,
    [Parameter(Mandatory = $true)]
    [ValidateSet('PENDING', 'PASS', 'FAIL', 'BLOCKED')]
    [string]$Result,
    [string]$EvidencePath,
    [string]$Reviewer = 'UNASSIGNED',
    [string]$Notes = ''
)

$ErrorActionPreference = 'Stop'
$batchRoot = [IO.Path]::GetFullPath($BatchPath)
$metadataPath = Join-Path $batchRoot 'MILL_BATCH.json'
if (-not (Test-Path -LiteralPath $metadataPath -PathType Leaf)) {
    throw "MILL_BATCH.json is missing: $metadataPath"
}

$metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
if ($metadata.status -eq 'PROMOTED') {
    throw 'A promoted batch is immutable. Create a new batch for subsequent work.'
}

$resolvedEvidence = ''
if ($Result -ne 'PENDING') {
    if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
        throw "$Result requires an evidence path."
    }
    if ([IO.Path]::IsPathRooted($EvidencePath) -or $EvidencePath -match '(^|[\\/])\.\.([\\/]|$)') {
        throw 'EvidencePath must be a safe path relative to the batch root.'
    }
    $resolvedEvidence = [IO.Path]::GetFullPath((Join-Path $batchRoot $EvidencePath))
    $batchPrefix = $batchRoot.TrimEnd('\') + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedEvidence.StartsWith($batchPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'EvidencePath resolves outside the batch root.'
    }
    if (-not (Test-Path -LiteralPath $resolvedEvidence -PathType Leaf)) {
        throw "Gate evidence file is missing: $resolvedEvidence"
    }
}

$metadata.gates.PSObject.Properties[$Gate].Value = $Result
$metadata.status = switch ($Result) {
    'PASS' { if ($Gate -eq 'live') { 'DECISION_PENDING' } else { 'IN_PROGRESS' } }
    'PENDING' { 'IN_PROGRESS' }
    default { 'HELD' }
}
if ($metadata.decision.value -eq 'PROMOTE') {
    $metadata.decision.value = 'HOLD'
    $metadata.decision.authorized = $false
    $metadata.decision.authorized_by = $null
    $metadata.decision.approval_evidence_path = $null
}
$metadata.decision.updated_utc = [DateTime]::UtcNow.ToString('o')

[IO.File]::WriteAllText(
    $metadataPath,
    ($metadata | ConvertTo-Json -Depth 8) + "`n",
    [Text.UTF8Encoding]::new($false)
)

[pscustomobject]@{
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    gate = $Gate
    result = $Result
    evidence_path = if ($Result -eq 'PENDING') { '' } else { $EvidencePath.Replace('\', '/') }
    reviewer = $Reviewer
    notes = $Notes
} | Export-Csv -LiteralPath (Join-Path $batchRoot 'GATE_LEDGER.csv') -Append -NoTypeInformation -Encoding utf8

& (Join-Path $PSScriptRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null

[ordered]@{
    result = 'GATE_RECORDED'
    batch_path = $batchRoot
    gate = $Gate
    gate_result = $Result
    evidence_path = $EvidencePath
    status = $metadata.status
    decision = $metadata.decision.value
} | ConvertTo-Json -Depth 5
