[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath
)

$ErrorActionPreference = 'Stop'

$batchRoot = [IO.Path]::GetFullPath($BatchPath)
if (-not (Test-Path -LiteralPath $batchRoot -PathType Container)) {
    throw "Batch directory is missing: $batchRoot"
}

$failures = [Collections.Generic.List[string]]::new()
$requiredDirectories = @(
    'source', 'candidate', 'harness', 'package', 'audit', 'rollback',
    'evidence/source', 'evidence/candidate', 'evidence/static', 'evidence/compiler',
    'evidence/package', 'evidence/live', 'evidence/decision'
)
$requiredFiles = @(
    'README.md', 'MILL_BATCH.json', 'SOURCE_INVENTORY.csv',
    'CLAIM_LEDGER.csv', 'GATE_LEDGER.csv', 'DECISION_LEDGER.csv',
    'VALIDATION_PLAN.csv', 'LIVE_RESULTS.csv', 'DECISION.md',
    'ROLLBACK.md', 'ERROR_LOG.md', 'SENTINEL_REGISTRY.json',
    'REFERENCE_REGISTRY.json', 'GLUE_LEDGER.csv', 'MANIFEST.sha256'
)

foreach ($relative in $requiredDirectories) {
    if (-not (Test-Path -LiteralPath (Join-Path $batchRoot $relative) -PathType Container)) {
        $failures.Add("Missing required directory: $relative")
    }
}
foreach ($relative in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $batchRoot $relative) -PathType Leaf)) {
        $failures.Add("Missing required file: $relative")
    }
}

$reparsePoints = @(
    Get-ChildItem -LiteralPath $batchRoot -Recurse -Force |
        Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }
)
if ($reparsePoints.Count -gt 0) {
    $failures.Add("Reparse points are not allowed inside a mill batch: $($reparsePoints.Count)")
}

$expectedHeaders = [ordered]@{
    'SOURCE_INVENTORY.csv' = 'identifier,location,type,version_status,authority,accessibility,integrity,relevance'
    'CLAIM_LEDGER.csv' = 'claim_id,claim,state,source,evidence,notes'
    'GATE_LEDGER.csv' = 'timestamp_utc,gate,result,evidence_path,reviewer,notes'
    'DECISION_LEDGER.csv' = 'timestamp_utc,decision,authorized_by,approval_evidence_path,notes'
    'VALIDATION_PLAN.csv' = 'test_id,gate,claim,method,discriminator,expected,evidence_path,status'
    'LIVE_RESULTS.csv' = 'test_id,scene_or_condition,setting_or_view,expected,observed,result,evidence_path,notes'
    'GLUE_LEDGER.csv' = 'glue_id,producer_ref,consumer_ref,input_contract,output_contract,authority_ceiling,normalization,loss_policy,idempotency,status,evidence'
}
foreach ($entry in $expectedHeaders.GetEnumerator()) {
    $path = Join-Path $batchRoot $entry.Key
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $header = Get-Content -LiteralPath $path -TotalCount 1
        if ($header -ne $entry.Value) {
            $failures.Add("Unexpected ledger header: $($entry.Key)")
        }
    }
}

$metadata = $null
$metadataPath = Join-Path $batchRoot 'MILL_BATCH.json'
if (Test-Path -LiteralPath $metadataPath -PathType Leaf) {
    try {
        $metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
    }
    catch {
        $failures.Add("MILL_BATCH.json is invalid JSON: $($_.Exception.Message)")
    }
}

$requiredGateNames = @('source_freeze', 'candidate', 'static', 'compiler', 'package', 'live')
$allowedGateResults = @('PENDING', 'PASS', 'FAIL', 'BLOCKED')
if ($null -ne $metadata) {
    if ($metadata.schema_version -ne 2) {
        $failures.Add("Unsupported schema version: $($metadata.schema_version)")
    }
    if ($metadata.batch_id -ne (Split-Path -Leaf $batchRoot)) {
        $failures.Add('Batch ID does not match the directory name.')
    }
    if ($metadata.truth_state -notin @(
        'GENERATED_SYNTHESIS', 'SOURCE', 'DERIVED', 'VERIFIED_EXTERNAL',
        'ACCEPTED_CANON'
    )) {
        $failures.Add("Unsupported truth state: $($metadata.truth_state)")
    }
    foreach ($gate in $requiredGateNames) {
        $property = $metadata.gates.PSObject.Properties[$gate]
        if ($null -eq $property) {
            $failures.Add("Missing gate metadata: $gate")
        }
        elseif ($property.Value -notin $allowedGateResults) {
            $failures.Add("Invalid gate result for $gate`: $($property.Value)")
        }
    }

    $decision = $metadata.decision.value
    if ($decision -notin @('HOLD', 'REVISE', 'REJECT', 'PROMOTE')) {
        $failures.Add("Unsupported decision: $decision")
    }
    if ($decision -eq 'PROMOTE' -or $metadata.status -eq 'PROMOTED') {
        $notPassed = @(
            $requiredGateNames | Where-Object {
                $metadata.gates.PSObject.Properties[$_].Value -ne 'PASS'
            }
        )
        if ($notPassed.Count -gt 0) {
            $failures.Add("Promotion has non-passing gates: $($notPassed -join ', ')")
        }
        if ($metadata.decision.authorized -ne $true) {
            $failures.Add('Promotion is not explicitly authorized.')
        }
        if ([string]::IsNullOrWhiteSpace($metadata.decision.authorized_by)) {
            $failures.Add('Promotion has no authorizer.')
        }
        if ([string]::IsNullOrWhiteSpace($metadata.decision.approval_evidence_path)) {
            $failures.Add('Promotion has no approval-evidence path.')
        }
    }
}

$sentinelRegistry = $null
$sentinelPath = Join-Path $batchRoot 'SENTINEL_REGISTRY.json'
if (Test-Path -LiteralPath $sentinelPath -PathType Leaf) {
    try {
        $sentinelRegistry = Get-Content -LiteralPath $sentinelPath -Raw | ConvertFrom-Json
        $sentinelIds = @($sentinelRegistry.sentinels | ForEach-Object { $_.sentinel_id })
        if ($sentinelIds.Count -ne @($sentinelIds | Sort-Object -Unique).Count) {
            $failures.Add('Sentinel IDs must be unique.')
        }
        foreach ($requiredSentinel in @(
            'PENDING_DEFINITION', 'UNKNOWN', 'BLOCKED', 'INTEGRITY_FAILURE',
            'OWNERSHIP_AMBIGUOUS', 'TERMINAL_FINISHED', 'TERMINAL_PROBLEM',
            '__CANNOT_NULL__'
        )) {
            if ($requiredSentinel -notin $sentinelIds) {
                $failures.Add("Missing required sentinel: $requiredSentinel")
            }
        }
        if ($sentinelRegistry.rules.no_silent_coercion -ne $true) {
            $failures.Add('Sentinel registry must prohibit silent coercion.')
        }
    }
    catch {
        $failures.Add("SENTINEL_REGISTRY.json is invalid: $($_.Exception.Message)")
    }
}

$referenceRegistry = $null
$referenceById = @{}
$referencePath = Join-Path $batchRoot 'REFERENCE_REGISTRY.json'
if (Test-Path -LiteralPath $referencePath -PathType Leaf) {
    try {
        $referenceRegistry = Get-Content -LiteralPath $referencePath -Raw | ConvertFrom-Json
        $allowedTypes = @($referenceRegistry.allowed_reference_types)
        $allowedStates = @($referenceRegistry.allowed_resolution_states)
        foreach ($reference in @($referenceRegistry.references)) {
            if ([string]::IsNullOrWhiteSpace($reference.reference_id)) {
                $failures.Add('Reference ID cannot be empty.')
                continue
            }
            if ($referenceById.ContainsKey($reference.reference_id)) {
                $failures.Add("Duplicate reference ID: $($reference.reference_id)")
                continue
            }
            $referenceById[$reference.reference_id] = $reference
            if ($reference.reference_type -notin $allowedTypes) {
                $failures.Add("Invalid reference type for $($reference.reference_id): $($reference.reference_type)")
            }
            if ($reference.resolution_state -notin $allowedStates) {
                $failures.Add("Invalid reference state for $($reference.reference_id): $($reference.resolution_state)")
            }
            if (
                $reference.reference_type -eq 'VERSION_PINNED' -and
                [string]::IsNullOrWhiteSpace($reference.digest)
            ) {
                $failures.Add("Version-pinned reference lacks a digest: $($reference.reference_id)")
            }
            if (
                $reference.resolution_state -eq 'RESOLVED' -and
                [string]::IsNullOrWhiteSpace($reference.interpretation_context)
            ) {
                $failures.Add("Resolved reference lacks interpretation context: $($reference.reference_id)")
            }
        }
    }
    catch {
        $failures.Add("REFERENCE_REGISTRY.json is invalid: $($_.Exception.Message)")
    }
}

$gluePath = Join-Path $batchRoot 'GLUE_LEDGER.csv'
if (Test-Path -LiteralPath $gluePath -PathType Leaf) {
    try {
        foreach ($edge in @(Import-Csv -LiteralPath $gluePath)) {
            if ($edge.status -notin @('DRAFT', 'PASS', 'BLOCKED', 'REJECTED')) {
                $failures.Add("Invalid glue status for $($edge.glue_id): $($edge.status)")
            }
            if ($edge.authority_ceiling -notin @(
                'SOURCE_ONLY', 'DERIVED_ONLY', 'WORKING_CONTRACT', 'ACCEPTED_CANON'
            )) {
                $failures.Add("Invalid glue authority ceiling for $($edge.glue_id): $($edge.authority_ceiling)")
            }
            if ($edge.status -eq 'PASS') {
                foreach ($referenceId in @($edge.producer_ref, $edge.consumer_ref)) {
                    if (-not $referenceById.ContainsKey($referenceId)) {
                        $failures.Add("PASS glue edge has unknown reference: $referenceId")
                    }
                    elseif ($referenceById[$referenceId].resolution_state -ne 'RESOLVED') {
                        $failures.Add("PASS glue edge has unresolved reference: $referenceId")
                    }
                }
                if ([string]::IsNullOrWhiteSpace($edge.evidence)) {
                    $failures.Add("PASS glue edge lacks evidence: $($edge.glue_id)")
                }
                elseif (
                    [IO.Path]::IsPathRooted($edge.evidence) -or
                    $edge.evidence -match '(^|[\\/])\.\.([\\/]|$)'
                ) {
                    $failures.Add("PASS glue edge has unsafe evidence path: $($edge.glue_id)")
                }
                else {
                    $glueEvidence = [IO.Path]::GetFullPath((Join-Path $batchRoot $edge.evidence))
                    $batchPrefix = $batchRoot.TrimEnd('\') + [IO.Path]::DirectorySeparatorChar
                    if (
                        -not $glueEvidence.StartsWith($batchPrefix, [StringComparison]::OrdinalIgnoreCase) -or
                        -not (Test-Path -LiteralPath $glueEvidence -PathType Leaf)
                    ) {
                        $failures.Add("PASS glue edge evidence is missing or outside batch: $($edge.glue_id)")
                    }
                }
            }
        }
    }
    catch {
        $failures.Add("GLUE_LEDGER.csv is invalid: $($_.Exception.Message)")
    }
}

$manifestPass = $false
try {
    $manifestJson = & (Join-Path $PSScriptRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot
    $manifestResult = $manifestJson | ConvertFrom-Json
    $manifestPass = $manifestResult.result -eq 'PASS'
}
catch {
    $failures.Add("Manifest verification failed: $($_.Exception.Message)")
}

$result = [ordered]@{
    result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
    batch_path = $batchRoot
    structure_pass = @(
        $requiredDirectories | Where-Object {
            -not (Test-Path -LiteralPath (Join-Path $batchRoot $_) -PathType Container)
        }
    ).Count -eq 0
    manifest_pass = $manifestPass
    gate_logic_pass = -not (@($failures | Where-Object { $_ -match 'gate|Promotion|decision' }).Count)
    failures = @($failures)
    evidence_boundary = 'PASS proves factory structure and internal consistency only.'
}

$result | ConvertTo-Json -Depth 7
if ($failures.Count -gt 0) {
    throw "Mill batch validation failed with $($failures.Count) error(s)."
}
