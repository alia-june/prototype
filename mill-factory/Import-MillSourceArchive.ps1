[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath,
    [Parameter(Mandatory = $true)]
    [string]$ArchivePath,
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')]
    [string]$SourceId,
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Relevance,
    [switch]$Expand
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$batchRoot = [IO.Path]::GetFullPath($BatchPath)
$archiveSource = [IO.Path]::GetFullPath($ArchivePath)
if (-not (Test-Path -LiteralPath $batchRoot -PathType Container)) {
    throw "Batch directory is missing: $batchRoot"
}
if (-not (Test-Path -LiteralPath $archiveSource -PathType Leaf)) {
    throw "Source archive is missing: $archiveSource"
}
if ([IO.Path]::GetExtension($archiveSource) -ne '.zip') {
    throw 'Only ZIP source archives are supported by this intake tool.'
}

$metadataPath = Join-Path $batchRoot 'MILL_BATCH.json'
$metadata = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
if ($metadata.status -eq 'PROMOTED') {
    throw 'A promoted batch is immutable. Create a new batch for subsequent work.'
}

$packageRoot = Join-Path $batchRoot 'source\packages'
$expandedParent = Join-Path $batchRoot 'source\expanded'
$expandedRoot = Join-Path $expandedParent $SourceId
foreach ($directory in @($packageRoot, $expandedParent)) {
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory | Out-Null
    }
}

$archiveName = [IO.Path]::GetFileName($archiveSource)
$archiveDestination = Join-Path $packageRoot $archiveName
$inventoryPath = Join-Path $batchRoot "evidence\source\$SourceId-archive-inventory.json"
if (Test-Path -LiteralPath $archiveDestination) {
    throw "Refusing to overwrite imported source archive: $archiveDestination"
}
if (Test-Path -LiteralPath $inventoryPath) {
    throw "Refusing to overwrite source inventory evidence: $inventoryPath"
}
if ($Expand -and (Test-Path -LiteralPath $expandedRoot)) {
    throw "Refusing to overwrite expanded source: $expandedRoot"
}

$archiveHash = (Get-FileHash -LiteralPath $archiveSource -Algorithm SHA256).Hash
$archive = [IO.Compression.ZipFile]::OpenRead($archiveSource)
try {
    $entries = @($archive.Entries | Where-Object { -not [string]::IsNullOrEmpty($_.Name) })
    $unsafe = @(
        $entries | Where-Object {
            $_.FullName -match '(^/|\\|(^|/)\.\.(/|$)|^[A-Za-z]:)'
        }
    )
    if ($unsafe.Count -gt 0) {
        throw "Archive contains unsafe paths: $($unsafe.FullName -join ', ')"
    }
    $duplicates = @($entries.FullName | Group-Object | Where-Object Count -gt 1)
    if ($duplicates.Count -gt 0) {
        throw "Archive contains duplicate file paths: $($duplicates.Name -join ', ')"
    }

    $entryRecords = foreach ($entry in $entries) {
        [ordered]@{
            path = $entry.FullName
            bytes = $entry.Length
            compressed_bytes = $entry.CompressedLength
            kind = if ($entry.Name -match '(?i)\.(py|ps1|js|vbs|bat|cmd|exe|dll|com|scr)$') {
                'CODE_OR_EXECUTABLE'
            }
            elseif ($entry.Name -match '(?i)\.(zip|7z|rar|tar|gz)$') {
                'NESTED_ARCHIVE'
            }
            else {
                'DOCUMENT_OR_DATA'
            }
        }
    }

    Copy-Item -LiteralPath $archiveSource -Destination $archiveDestination

    if ($Expand) {
        New-Item -ItemType Directory -Path $expandedRoot | Out-Null
        $expandedPrefix = $expandedRoot.TrimEnd('\') + [IO.Path]::DirectorySeparatorChar
        foreach ($entry in $entries) {
            $relative = $entry.FullName.Replace('/', '\')
            $target = [IO.Path]::GetFullPath((Join-Path $expandedRoot $relative))
            if (-not $target.StartsWith($expandedPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw "Archive entry resolves outside the expansion root: $($entry.FullName)"
            }
            $parent = Split-Path -Parent $target
            if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
                New-Item -ItemType Directory -Path $parent -Force | Out-Null
            }
            $input = $entry.Open()
            $output = [IO.File]::Open(
                $target,
                [IO.FileMode]::CreateNew,
                [IO.FileAccess]::Write,
                [IO.FileShare]::None
            )
            try {
                $input.CopyTo($output)
            }
            finally {
                $output.Dispose()
                $input.Dispose()
            }
        }
    }
}
finally {
    $archive.Dispose()
}

$inventory = [ordered]@{
    schema_version = 1
    source_id = $SourceId
    supplied_path = $archiveSource
    stored_path = $archiveDestination.Substring($batchRoot.Length + 1).Replace('\', '/')
    sha256 = $archiveHash
    archive_bytes = (Get-Item -LiteralPath $archiveSource).Length
    entry_count = $entryRecords.Count
    uncompressed_bytes = ($entryRecords | Measure-Object bytes -Sum).Sum
    unsafe_paths = 0
    nested_archives = @($entryRecords | Where-Object kind -eq 'NESTED_ARCHIVE').Count
    code_or_executable_entries = @($entryRecords | Where-Object kind -eq 'CODE_OR_EXECUTABLE').Count
    expanded = [bool]$Expand
    execution_status = 'NOT_EXECUTED'
    authority = 'SUPPLIED_SOURCE'
    relevance = $Relevance
    entries = @($entryRecords)
}
[IO.File]::WriteAllText(
    $inventoryPath,
    ($inventory | ConvertTo-Json -Depth 8) + "`n",
    [Text.UTF8Encoding]::new($false)
)

[pscustomobject]@{
    identifier = $SourceId
    location = $inventory.stored_path
    type = 'ZIP_SOURCE_ARCHIVE'
    version_status = 'SUPPLIED_SNAPSHOT'
    authority = 'SUPPLIED_SOURCE'
    accessibility = if ($Expand) { 'READABLE_EXPANDED' } else { 'READABLE_ARCHIVE' }
    integrity = "SHA256:$archiveHash"
    relevance = $Relevance
} | Export-Csv -LiteralPath (Join-Path $batchRoot 'SOURCE_INVENTORY.csv') -Append -NoTypeInformation -Encoding utf8

& (Join-Path $PSScriptRoot 'Update-MillManifest.ps1') -BatchPath $batchRoot -Write | Out-Null

[ordered]@{
    result = 'SOURCE_IMPORTED'
    batch_path = $batchRoot
    source_id = $SourceId
    archive_sha256 = $archiveHash
    entries = $entryRecords.Count
    unsafe_paths = 0
    nested_archives = $inventory.nested_archives
    code_or_executable_entries = $inventory.code_or_executable_entries
    expanded = [bool]$Expand
    execution_status = 'NOT_EXECUTED'
    inventory_evidence = $inventoryPath.Substring($batchRoot.Length + 1).Replace('\', '/')
} | ConvertTo-Json -Depth 6
