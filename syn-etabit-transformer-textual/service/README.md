# Syn-Etabit Transformer — Textual

This is the current compatibility implementation for **Syn-Etabit Transformer — Textual**, the canonical prospective product brand. **Syn means synthetic.** The Python distribution remains `docstream-cpu`, the module remains `docstream_cpu`, the CLI remains `docstream-local`, protocol identifiers remain `docstream.*`, and local state remains under `.docstream`. Docstream and Strmdocx are preserved where they identify the actual historical implementation and evidence; this bounded rebrand does not silently rewrite those records or break those interfaces.

This package contains the CPU reference model and a durable local MCP service:
immutable semantic snapshots, typed transformations, logical output streams,
an explainable reducer, SQLite receipts/recovery and a thin CLI. Importing the
library starts no listener. M3 adds project-local Chromium rendering, PNG/PDF
artifacts, cache reuse and an explicit rendered-commit path. M4a adds Markdown
and DOCX import/export, inline formatting, nested lists, simple tables, managed
PNG/JPEG images and conversion-loss receipts. Current version: 0.2.0.dev4.

The forward product direction is Markdown-first, JSON-governed and reference-native. A final internal document is intended to cross an **Eject → Transform → Ejection** boundary: emit a complete immutable conversion package, transform it through an external target-format adapter, and retain the resulting artifact and receipt separately. That direction is not yet a runtime migration. The implemented M4a Markdown/DOCX adapters and their recorded limitations remain part of this compatibility service until separately approved work replaces or reclassifies them.

The intended workflow is a structured service request: import a source, inspect
its content, submit an ordered transformation batch, preview or commit a new
stream, and retrieve an export. Ordinary callers do not write rendering scripts.
Agentic-control registration and activation remain the final development stage.

The original release is preserved under `baseline/docstream-0.1.0/`. New work is
under `src/docstream_cpu/`; these namespaces remain separate.

Use the package through `CpuModel`, `parse_batch`, `plan`, `execute` and
`reference_execute`. `CpuModel.stage` validates a complete batch and catalogs
every logical output. `inspect(..., content=True)` materializes a recorded
prefix without advancing the head. `commit_semantic` explicitly advances only
the in-memory head. Its result has no durability or visual-render guarantee.

For the prepared development environment, from this directory:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The local venv inherits bundled runtime packages and installs this package in
editable mode. M2 dependencies are installed locally. It is not a standalone
release environment. Historical CPU evidence is in docs/M0_M1_VALIDATION.md;
service evidence is in docs/M2_VALIDATION.md. docs/M2_SERVICE_CONTRACT.md describes
foreground startup, tokens, tools and durable request behavior.

Current rendering additions and limits are in docs/M3_RENDERING_CONTRACT.md;
actual browser/visual evidence is in docs/M3_VALIDATION.md. Use a registered font
(Arial, Times New Roman or Consolas on this host); the inherited Aptos default
is not silently substituted. A missing requested font returns an explicit error.

Batch payloads use `docstream.batch/1`, `base_sha256`, and an ordered `operations`
array with unique operation IDs. Each kind is packaged code; requests cannot
contain executable Python or shell actions. See `docs/CPU_CONTRACT.md` for the
operation semantics and examples. The initial ingestion helper preserves UTF-8
bytes and treats decoded content as one literal block; explicit Markdown parsing
now uses the separate format import operation. Run the combined retained service
validation with `.\.venv\Scripts\python.exe tests\run_m2_validation.py`. The M2
service uses a distinct persistent adapter while preserving CpuModel as a pure
in-memory reference. Run current combined validation with
`.\.venv\Scripts\python.exe tests\run_m3_validation.py`. The maintained
`examples\render_example.py` exercises the complete semantic/rendered-commit
workflow without caller-authored rendering code. No Codex connection or automatic
startup is configured.

For current format behavior, read `docs/M4_FORMAT_CONTRACT.md`; actual results
are in `docs/M4_VALIDATION.md`. The service exposes ten tools, including
`docstream_import` and `docstream_export`. `docstream_inspect` can navigate rich
content with `section: structure` and an explicit field/index path. Imports and
exports reject detected conversion losses by default; accepting losses is an
explicit request option whose diagnostics remain in the receipt.

Version-one snapshots and hashes remain unchanged. Version two adds spans,
tables, images and nested lists. `replace_block` changes a complete rich block
under its input hash guard; `replace_text` cannot erase rich structure. Code text
in version two honors semantic font inheritance. Assign a monospace font
explicitly where it is intended.

Run the current combined suite with:

```powershell
.\.venv\Scripts\python.exe tests\run_m4_validation.py
```

The maintained `examples\format_example.py` exercises import, exports, a
reduced font cycle, preview and rendered commit through application services.
It writes its bounded example store under `.docstream/m4-validation/` and an
evidence record under `service/docs/`. Its small blue image is a controlled test
fixture. It does not register an agent host or leave a listener running.

Markdown export is a ZIP containing Markdown, document-property/image metadata
and its assets. DOCX support is an explicit semantic subset, with conservative
loss diagnostics; Word pagination and unrestricted document compatibility are
not certified. Database schema remains 2 and M4a requires no migration. The
project venv still inherits bundled packages; standalone installation and
upgrade/release packaging remain subsequent work.

## Rigid fuzzy and torture harness

Use the maintained harness for current validation and separate run records:

```powershell
.\.venv\Scripts\python.exe -m docstream_cpu.harness all
.\.venv\Scripts\python.exe -m docstream_cpu.harness rigid
.\.venv\Scripts\python.exe -m docstream_cpu.harness fuzzy --seed 20261029
.\.venv\Scripts\python.exe -m docstream_cpu.harness torture
```

Each invocation creates a new folder under `.docstream/harness-runs/` at the
workspace root. Read REPORT.md for the outcome, summary.json for structured
results, and the mode's inputs/failures folders for replay data. `all --replay`
selects the appropriate mode for a saved case. Existing run IDs and visual
baselines are never overwritten by a normal run.

The current product outcome is **failed**: rigid and bounded torture checks
pass, while the 500-case fuzzy run finds three character/conversion groups.
The harness is delivered and its own tests pass. Read
`docs/HARNESS_CONTRACT.md`, `docs/HARNESS_VALIDATION.md` and
`docs/HARNESS_FINDINGS.md` before treating any earlier milestone green result
as general product acceptance. Product behavior was preserved so the failures
remain visible. Agentic-control integration is still the final stage.
