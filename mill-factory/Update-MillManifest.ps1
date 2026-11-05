[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BatchPath,
    [switch]$Write
)

$ErrorActionPreference = 'Stop'

$batchRoot = [IO.Path]::GetFullPath($BatchPath)
if (-not (Test-Path -LiteralPath $batchRoot -PathType Container)) {
    throw "Batch directory is missing: $batchRoot"
}

$manifestPath = Join-Path $batchRoot 'MANIFEST.sha256'
$files = @(
    Get-ChildItem -LiteralPath $batchRoot -Recurse -File -Force |
        Where-Object { $_.FullName -ne $manifestPath } |
        Sort-Object FullName
)

$actual = [ordered]@{}
foreach ($file in $files) {
    $relative = $file.FullName.Substring($batchRoot.Length + 1).Replace('\', '/')
    $actual[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
}

if ($Write) {
    $lines = foreach ($entry in $actual.GetEnumerator()) {
        "$($entry.Value)  $($entry.Key)"
    }
    [IO.File]::WriteAllLines(
        $manifestPath,
        $lines,
        [Text.UTF8Encoding]::new($false)
    )
    [ordered]@{
        result = 'MANIFEST_WRITTEN'
        batch_path = $batchRoot
        manifest_path = $manifestPath
        entries = $lines.Count
    } | ConvertTo-Json -Depth 4
    return
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Manifest is missing: $manifestPath"
}

$expected = [ordered]@{}
$malformed = [Collections.Generic.List[string]]::new()
foreach ($line in Get-Content -LiteralPath $manifestPath) {
    if ($line -notmatch '^([0-9A-Fa-f]{64})  (.+)$') {
        $malformed.Add($line)
        continue
    }
    $relative = $Matches[2]
    if ($expected.Contains($relative)) {
        $malformed.Add("DUPLICATE: $relative")
        continue
    }
    $expected[$relative] = $Matches[1].ToUpperInvariant()
}

$missing = @($expected.Keys | Where-Object { -not $actual.Contains($_) })
$unrecorded = @($actual.Keys | Where-Object { -not $expected.Contains($_) })
$mismatched = @(
    $actual.Keys |
        Where-Object {
            $expected.Contains($_) -and $expected[$_] -ne $actual[$_]
        }
)

$result = [ordered]@{
    result = if (
        $malformed.Count -eq 0 -and
        $missing.Count -eq 0 -and
        $unrecorded.Count -eq 0 -and
        $mismatched.Count -eq 0
    ) { 'PASS' } else { 'FAIL' }
    batch_path = $batchRoot
    expected_entries = $expected.Count
    actual_entries = $actual.Count
    malformed_lines = @($malformed)
    missing_files = $missing
    unrecorded_files = $unrecorded
    hash_mismatches = $mismatched
}

$result | ConvertTo-Json -Depth 6
if ($result.result -ne 'PASS') {
    throw 'Mill manifest verification failed.'
}
