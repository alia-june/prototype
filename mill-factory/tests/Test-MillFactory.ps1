[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$factoryRoot = Split-Path -Parent $PSScriptRoot
$temporaryRoot = Join-Path (
    [IO.Path]::GetTempPath()
) ('mill-factory-test-' + [guid]::NewGuid().ToString('N'))
$millRoot = Join-Path $temporaryRoot 'mill'
$checks = [Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )
    $checks.Add([pscustomobject]@{
        name = $Name
        passed = $Passed
        detail = $Detail
    })
}

try {
    New-Item -ItemType Directory -Path $temporaryRoot | Out-Null

    Push-Location $temporaryRoot
    try {
        $portableJson = & (Join-Path $factoryRoot 'New-MillBatch.ps1') `
            -Slug 'portable-default' `
            -Title 'Portable Default' `
            -Scope 'Verify that the default mill root follows the working directory.' `
            -Date '2026-11-04'
        $portable = $portableJson | ConvertFrom-Json
    }
    finally {
        Pop-Location
    }
    Add-Check 'portable_default_root' (
        $portable.batch_path -eq (Join-Path $temporaryRoot 'mill\portable-default-2026-11-04')
    ) 'Default output resolved beneath the caller working directory.'

    $createdJson = & (Join-Path $factoryRoot 'New-MillBatch.ps1') `
        -Slug 'factory-self-test' `
        -Title 'Factory Self Test' `
        -Scope 'Disposable positive and negative controls.' `
        -Date '2026-11-02' `
        -OutputRoot $millRoot
    $created = $createdJson | ConvertFrom-Json
    $batchRoot = $created.batch_path
    Add-Check 'create_batch' ($created.result -eq 'BATCH_CREATED') $batchRoot

    $initialJson = & (Join-Path $factoryRoot 'Test-MillBatch.ps1') -BatchPath $batchRoot
    $initial = $initialJson | ConvertFrom-Json
    Add-Check 'initial_validation' ($initial.result -eq 'PASS') 'Fresh scaffold validates.'

    Add-Content -LiteralPath (Join-Path $batchRoot 'GLUE_LEDGER.csv') -Value (
        'bad-edge,missing-producer,missing-consumer,v1,v1,WORKING_CONTRACT,none,none,idempotent,PASS,evidence/static/bad.txt'
    )
    & (Join-Path $factoryRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null
    $unresolvedGlueRejected = $false
    try {
        & (Join-Path $factoryRoot 'Test-MillBatch.ps1') -BatchPath $batchRoot | Out-Null
    }
    catch {
        $unresolvedGlueRejected = $_.Exception.Message -match 'validation failed'
    }
    Add-Check 'unresolved_glue_refusal' $unresolvedGlueRejected 'PASS glue cannot consume unknown references.'
    Copy-Item -LiteralPath (Join-Path $factoryRoot 'templates/GLUE_LEDGER.csv') `
        -Destination (Join-Path $batchRoot 'GLUE_LEDGER.csv') -Force
    & (Join-Path $factoryRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null

    $duplicateRefused = $false
    try {
        & (Join-Path $factoryRoot 'New-MillBatch.ps1') `
            -Slug 'factory-self-test' `
            -Title 'Factory Self Test' `
            -Scope 'Duplicate refusal control.' `
            -Date '2026-11-02' `
            -OutputRoot $millRoot | Out-Null
    }
    catch {
        $duplicateRefused = $_.Exception.Message -match 'Refusing to overwrite'
    }
    Add-Check 'duplicate_refusal' $duplicateRefused 'Existing batch was not overwritten.'

    Add-Content -LiteralPath (Join-Path $batchRoot 'README.md') -Value "`nTAMPER"
    $tamperDetected = $false
    try {
        & (Join-Path $factoryRoot 'Test-MillBatch.ps1') -BatchPath $batchRoot | Out-Null
    }
    catch {
        $tamperDetected = $_.Exception.Message -match 'validation failed'
    }
    Add-Check 'manifest_tamper_detection' $tamperDetected 'Unmanifested content change was rejected.'

    & (Join-Path $factoryRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null
    $revalidatedJson = & (Join-Path $factoryRoot 'Test-MillBatch.ps1') -BatchPath $batchRoot
    $revalidated = $revalidatedJson | ConvertFrom-Json
    Add-Check 'intentional_manifest_refresh' ($revalidated.result -eq 'PASS') 'Intentional change was re-sealed.'

    $earlyPromotionRefused = $false
    try {
        & (Join-Path $factoryRoot 'Set-MillDecision.ps1') `
            -BatchPath $batchRoot `
            -Decision PROMOTE `
            -AuthorizedBy 'factory-self-test' `
            -ApprovalEvidencePath 'evidence/decision/APPROVAL.md' | Out-Null
    }
    catch {
        $earlyPromotionRefused = $_.Exception.Message -match 'gates are not PASS'
    }
    Add-Check 'fail_closed_promotion' $earlyPromotionRefused 'Promotion was refused while gates were pending.'

    $evidenceByGate = [ordered]@{
        source_freeze = 'evidence/source/SOURCE_FREEZE.txt'
        candidate = 'evidence/candidate/CANDIDATE.txt'
        static = 'evidence/static/STATIC.txt'
        compiler = 'evidence/compiler/COMPILER.txt'
        package = 'evidence/package/PACKAGE.txt'
        live = 'evidence/live/LIVE.txt'
    }
    foreach ($entry in $evidenceByGate.GetEnumerator()) {
        [IO.File]::WriteAllText(
            (Join-Path $batchRoot $entry.Value),
            "self-test evidence for $($entry.Key)`n",
            [Text.UTF8Encoding]::new($false)
        )
        & (Join-Path $factoryRoot 'Set-MillGate.ps1') `
            -BatchPath $batchRoot `
            -Gate $entry.Key `
            -Result PASS `
            -EvidencePath $entry.Value `
            -Reviewer 'factory-self-test' | Out-Null
    }
    [IO.File]::WriteAllText(
        (Join-Path $batchRoot 'evidence/decision/APPROVAL.md'),
        "# Disposable self-test approval`n",
        [Text.UTF8Encoding]::new($false)
    )
    & (Join-Path $factoryRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null
    $promotionJson = & (Join-Path $factoryRoot 'Set-MillDecision.ps1') `
        -BatchPath $batchRoot `
        -Decision PROMOTE `
        -AuthorizedBy 'factory-self-test' `
        -ApprovalEvidencePath 'evidence/decision/APPROVAL.md'
    $promotion = $promotionJson | ConvertFrom-Json
    $promotedJson = & (Join-Path $factoryRoot 'Test-MillBatch.ps1') -BatchPath $batchRoot
    $promoted = $promotedJson | ConvertFrom-Json
    Add-Check 'gated_promotion_record' (
        $promotion.authorized -eq $true -and $promoted.result -eq 'PASS'
    ) 'All gates and approval evidence were required.'

    $postPromotionMutationRefused = $false
    try {
        & (Join-Path $factoryRoot 'Set-MillGate.ps1') `
            -BatchPath $batchRoot `
            -Gate static `
            -Result PENDING | Out-Null
    }
    catch {
        $postPromotionMutationRefused = $_.Exception.Message -match 'immutable'
    }
    Add-Check 'promoted_batch_immutable' $postPromotionMutationRefused 'New work requires a new batch.'
}
finally {
    $resolvedTemporary = [IO.Path]::GetFullPath($temporaryRoot)
    $systemTemporary = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    if (
        $resolvedTemporary.StartsWith($systemTemporary, [StringComparison]::OrdinalIgnoreCase) -and
        (Split-Path -Leaf $resolvedTemporary) -like 'mill-factory-test-*' -and
        (Test-Path -LiteralPath $resolvedTemporary)
    ) {
        [IO.Directory]::Delete($resolvedTemporary, $true)
    }
}

$failed = @($checks | Where-Object { -not $_.passed })
$result = [ordered]@{
    result = if ($failed.Count -eq 0) { 'PASS' } else { 'FAIL' }
    passed = @($checks | Where-Object passed).Count
    failed = $failed.Count
    checks = @($checks)
}
$result | ConvertTo-Json -Depth 7
if ($failed.Count -gt 0) {
    throw "Mill factory self-test failed with $($failed.Count) error(s)."
}
