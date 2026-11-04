# Docstream Command Line Document Service

Docstream keeps Markdown as the canonical editable source and treats DOCX as an import or publishing format. It provides guarded regex editing, DOCX conversion, structural inspection, provenance logs, and a root-scoped localhost JSON service.

Status: generated implementation, locally tested. It is not accepted canon until you review and adopt it.

## Install on Windows

Python 3.10 or newer is required. Pandoc is recommended for the broadest DOCX compatibility; without it, Docstream uses its built-in standard-document converter.

```powershell
Set-Location path\to\docstream
.\install.ps1
.\.venv\Scripts\docstream.exe --help
```

If PowerShell script execution is restricted, run the equivalent commands directly:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
```

To use Pandoc, install it separately and ensure `pandoc` is on `PATH`, or pass `--pandoc C:\path\to\pandoc.exe`.

## Markdown First Workflow

```powershell
docstream new report.md --title "Quarterly Operations Report"

docstream edit report.md `
  --pattern '(?m)^Status:\s+Draft$' `
  --replacement 'Status: Final' `
  --expected 1 `
  --dry-run

docstream edit report.md `
  --pattern '(?m)^Status:\s+Draft$' `
  --replacement 'Status: Final' `
  --expected 1 `
  --backup

docstream inspect report.md --json
docstream publish report.md -o report.docx
```

## Import an Existing DOCX

```powershell
docstream import source.docx -o source.md
docstream edit source.md --pattern 'old phrase' --replacement 'new phrase' --expected 1 --backup
docstream publish source.md -o revised.docx
```

`--backend auto` prefers Pandoc and otherwise selects the native converter. Use `--backend pandoc` to require Pandoc or `--backend native` for deterministic standard-document conversion.

Pandoc is recommended for footnotes, citations, embedded media, and complex structure. The native backend supports titles and headings, paragraphs, ordered and unordered lists, blockquotes, fenced code, pipe tables, bold, italic, inline code, and visible hyperlink targets. Native DOCX import does not promise preservation of text boxes, fields, comments, tracked revisions, floating objects, or layout-specific Word features.

## Regex Editing Safety

- `--dry-run` prints the unified diff without writing.
- `--expected N` prevents a write unless exactly N matches are found.
- `--limit N` caps replacements.
- `--backup` writes `filename.md.bak` before the atomic replacement.
- Flags `i`, `m`, `s`, and `x` map to Python regular-expression flags.
- Replacements support capture syntax such as `\g<1>`.
- Successful mutations append a JSONL record under `.docstream/audit.jsonl`.

## Local Service

The service binds to `127.0.0.1` by default and rejects paths that escape its document root.

```powershell
docstream serve --root C:\Documents\Writing --port 8765
# Or, from the project directory:
.\start-service.ps1 -DocumentRoot C:\Documents\Writing
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/v1/health
```

Edit request:

```powershell
$body = @{
  path = 'report.md'
  pattern = '(?m)^Status:\s+Draft$'
  replacement = 'Status: Final'
  expected = 1
  backup = $true
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8765/v1/edit `
  -ContentType 'application/json' `
  -Body $body
```

POST endpoints are `/v1/new`, `/v1/inspect`, `/v1/edit`, `/v1/import`, and `/v1/publish`. Each accepts the same operation fields used by the CLI. The service is intentionally local and unauthenticated; do not expose it to a network without adding authentication and TLS.

## Verification Boundary

Docstream verifies file creation, hashes, atomic writes, count guards, root containment, and standard conversion behavior. A generated DOCX should still be rendered and visually reviewed before final delivery because structural success does not prove page-layout quality.

