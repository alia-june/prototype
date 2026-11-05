[CmdletBinding()]
param(
    [string]$WorkspaceRoot = (Get-Location).Path,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$Slug,
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Title,
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Scope,
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]$Date = [DateTime]::Now.ToString('yyyy-MM-dd'),
    [string]$OutputRoot,
    [string]$Owner = 'UNASSIGNED'
)

$ErrorActionPreference = 'Stop'

$parsedDate = [DateTime]::MinValue
if (-not [DateTime]::TryParseExact(
    $Date,
    'yyyy-MM-dd',
    [Globalization.CultureInfo]::InvariantCulture,
    [Globalization.DateTimeStyles]::None,
    [ref]$parsedDate
)) {
    throw "Date is not a real calendar date: $Date"
}

$millRoot = if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    Join-Path ([IO.Path]::GetFullPath($WorkspaceRoot)) 'mill'
}
else {
    [IO.Path]::GetFullPath($OutputRoot)
}

if (-not (Test-Path -LiteralPath $millRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $millRoot | Out-Null
}

$batchId = "$Slug-$Date"
$batchRoot = [IO.Path]::GetFullPath((Join-Path $millRoot $batchId))
$millPrefix = $millRoot.TrimEnd('\') + [IO.Path]::DirectorySeparatorChar
if (-not $batchRoot.StartsWith($millPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing batch path outside the mill root: $batchRoot"
}
if (Test-Path -LiteralPath $batchRoot) {
    throw "Refusing to overwrite existing batch: $batchRoot"
}

$directories = @(
    'source',
    'candidate',
    'harness',
    'package',
    'audit',
    'rollback',
    'evidence',
    'evidence/source',
    'evidence/candidate',
    'evidence/static',
    'evidence/compiler',
    'evidence/package',
    'evidence/live',
    'evidence/decision'
)

New-Item -ItemType Directory -Path $batchRoot | Out-Null
foreach ($relative in $directories) {
    New-Item -ItemType Directory -Path (Join-Path $batchRoot $relative) | Out-Null
}

$templateRoot = Join-Path $PSScriptRoot 'templates'
foreach ($name in @(
    'SOURCE_INVENTORY.csv',
    'CLAIM_LEDGER.csv',
    'GATE_LEDGER.csv',
    'DECISION_LEDGER.csv',
    'VALIDATION_PLAN.csv',
    'LIVE_RESULTS.csv',
    'ERROR_LOG.md',
    'SENTINEL_REGISTRY.json',
    'REFERENCE_REGISTRY.json',
    'GLUE_LEDGER.csv'
)) {
    Copy-Item -LiteralPath (Join-Path $templateRoot $name) -Destination (Join-Path $batchRoot $name)
}

function Write-Template {
    param(
        [string]$TemplateName,
        [string]$DestinationName
    )
    $content = Get-Content -LiteralPath (Join-Path $templateRoot $TemplateName) -Raw
    $content = $content.Replace('{{TITLE}}', $Title)
    $content = $content.Replace('{{BATCH_ID}}', $batchId)
    $content = $content.Replace('{{DATE}}', $Date)
    $content = $content.Replace('{{SCOPE}}', $Scope)
    [IO.File]::WriteAllText(
        (Join-Path $batchRoot $DestinationName),
        $content,
        [Text.UTF8Encoding]::new($false)
    )
}

Write-Template -TemplateName 'README.md.tmpl' -DestinationName 'README.md'
Write-Template -TemplateName 'DECISION.md.tmpl' -DestinationName 'DECISION.md'
Write-Template -TemplateName 'ROLLBACK.md.tmpl' -DestinationName 'ROLLBACK.md'

$metadata = [ordered]@{
    schema_version = 2
    factory_version = '0.2.0'
    batch_id = $batchId
    title = $Title
    scope = $Scope
    owner = $Owner
    created_utc = [DateTime]::UtcNow.ToString('o')
    truth_state = 'GENERATED_SYNTHESIS'
    status = 'INTAKE_OPEN'
    authority = 'WORKING_EVIDENCE'
    gates = [ordered]@{
        source_freeze = 'PENDING'
        candidate = 'PENDING'
        static = 'PENDING'
        compiler = 'PENDING'
        package = 'PENDING'
        live = 'PENDING'
    }
    decision = [ordered]@{
        value = 'HOLD'
        authorized = $false
        authorized_by = $null
        approval_evidence_path = $null
        updated_utc = [DateTime]::UtcNow.ToString('o')
    }
    evidence_boundary = 'Factory structure and recorded gates do not by themselves prove runtime behavior, visual acceptance, canon, or promotion.'
}

[IO.File]::WriteAllText(
    (Join-Path $batchRoot 'MILL_BATCH.json'),
    ($metadata | ConvertTo-Json -Depth 8) + "`n",
    [Text.UTF8Encoding]::new($false)
)

& (Join-Path $PSScriptRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null

[ordered]@{
    result = 'BATCH_CREATED'
    batch_id = $batchId
    batch_path = $batchRoot
    truth_state = $metadata.truth_state
    status = $metadata.status
    decision = $metadata.decision.value
    directories = $directories.Count
    manifest = 'MANIFEST.sha256'
} | ConvertTo-Json -Depth 5
