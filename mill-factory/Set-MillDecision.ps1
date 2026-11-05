[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath,
    [Parameter(Mandatory = $true)]
    [ValidateSet('HOLD', 'REVISE', 'REJECT', 'PROMOTE')]
    [string]$Decision,
    [string]$AuthorizedBy = '',
    [string]$ApprovalEvidencePath = '',
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

$requiredGates = @('source_freeze', 'candidate', 'static', 'compiler', 'package', 'live')
$authorized = $false
if ($Decision -eq 'PROMOTE') {
    $notPassed = @(
        $requiredGates | Where-Object {
            $metadata.gates.PSObject.Properties[$_].Value -ne 'PASS'
        }
    )
    if ($notPassed.Count -gt 0) {
        throw "Promotion refused; gates are not PASS: $($notPassed -join ', ')"
    }
    if ([string]::IsNullOrWhiteSpace($AuthorizedBy)) {
        throw 'Promotion requires a named authorizer.'
    }
    if ([string]::IsNullOrWhiteSpace($ApprovalEvidencePath) -or
        [IO.Path]::IsPathRooted($ApprovalEvidencePath) -or
        $ApprovalEvidencePath -match '(^|[\\/])\.\.([\\/]|$)') {
        throw 'Promotion requires a safe approval-evidence path relative to the batch.'
    }
    $resolvedApproval = [IO.Path]::GetFullPath((Join-Path $batchRoot $ApprovalEvidencePath))
    $batchPrefix = $batchRoot.TrimEnd('\') + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedApproval.StartsWith($batchPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $resolvedApproval -PathType Leaf)) {
        throw "Promotion approval evidence is missing or outside the batch: $ApprovalEvidencePath"
    }
    $authorized = $true
}

$metadata.decision.value = $Decision
$metadata.decision.authorized = $authorized
$metadata.decision.authorized_by = if ($authorized) { $AuthorizedBy } else { $null }
$metadata.decision.approval_evidence_path = if ($authorized) {
    $ApprovalEvidencePath.Replace('\', '/')
} else { $null }
$metadata.decision.updated_utc = [DateTime]::UtcNow.ToString('o')
$metadata.status = switch ($Decision) {
    'PROMOTE' { 'PROMOTED' }
    'REJECT' { 'REJECTED' }
    'REVISE' { 'REVISION_REQUIRED' }
    default { 'HELD' }
}
$metadata.truth_state = if ($Decision -eq 'PROMOTE') {
    'ACCEPTED_CANON'
} else {
    'GENERATED_SYNTHESIS'
}

[IO.File]::WriteAllText(
    $metadataPath,
    ($metadata | ConvertTo-Json -Depth 8) + "`n",
    [Text.UTF8Encoding]::new($false)
)

[pscustomobject]@{
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    decision = $Decision
    authorized_by = if ($authorized) { $AuthorizedBy } else { '' }
    approval_evidence_path = if ($authorized) { $ApprovalEvidencePath.Replace('\', '/') } else { '' }
    notes = $Notes
} | Export-Csv -LiteralPath (Join-Path $batchRoot 'DECISION_LEDGER.csv') -Append -NoTypeInformation -Encoding utf8

& (Join-Path $PSScriptRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null

[ordered]@{
    result = 'DECISION_RECORDED'
    batch_path = $batchRoot
    decision = $Decision
    authorized = $authorized
    status = $metadata.status
    truth_state = $metadata.truth_state
} | ConvertTo-Json -Depth 5
