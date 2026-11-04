# Docstream 0.1.0 — Complete project catalog

Assessment date: 2026-10-28 (America/New_York).

## Authorization and source boundary

The user approved the specific static catalog-and-assessment proposal with "yes" in this chat. Clearance covers inspecting every archive entry and producing PROJECT_CATALOG.md and PROJECT_ASSESSMENT.md in <source-workspace>. It does not approve extraction, installation, running project code or tests, implementation, service startup, or a release.

Governing instructions: the user's supplied production gate and project-local AGENTS.md. Project evidence: the supplied archive, especially README.md, STATUS.md, render-failure.txt, implementation files, and existing tests. ContextService material supplies working agreements, not Docstream requirements or execution authority.

Archive: <local-user-home>\Desktop\Inbox\docstream-0.1.0.zip

Archive SHA-256: `4acbdb5ee634ede3067fa2ad7c189afbd051365e6714b72ad03159fd4df8bf72`

All archive entries were enumerated and all 14 regular files were read directly from the ZIP. No extraction or project-code execution occurred. The archive has **15 entries: 14 files and one explicit directory entry**, totaling **48,961 uncompressed bytes**. This corrects the proposal's preliminary description of two directory entries. Directory paths implied by file names are distinct from explicit ZIP directory entries.

The entry table records SHA-256 of uncompressed entry bytes, not compressed ZIP member storage. The directory entry's hash is the empty-byte digest. These hashes establish the reviewed bytes; they do not authenticate authorship or independently validate historical claims.

## Exhaustive archive inventory

All paths below are relative to the ZIP prefix `docstream-0.1.0/`.

| Archive-relative path | Bytes | SHA-256 | Purpose |
| --- | ---: | --- | --- |
| `src/` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Explicit directory entry; no file content. |
| `install.ps1` | 606 | `171a5543dc03bc419972c31e78f1be1513301f3e8bfcecec78bfc39b33231ec3` | Windows virtual-environment creation, pip upgrade/package installation, and version invocation. |
| `LICENSE` | 1056 | `1126322e2cc8d165adc4c792eeb195717de2bcc7b39be1ce77959d78e87ef685` | MIT license text; copyright year 2026, without a named holder. |
| `pyproject.toml` | 485 | `8fd85946af5e47c1eea6d4b6f7811b4799a413107a83322cb89a3ef511126ec1` | setuptools build metadata, Python/dependency range, console entry point, src discovery. |
| `README.md` | 3950 | `f88e4a855c6281782f8d43ad5f0a9f31298295a88a810a5bfbe65129c04fa55e` | User-facing workflow, CLI/service examples, backend policy, and stated verification boundaries. |
| `render-failure.txt` | 428 | `d7ebb54fe096836082a59a805c357dc821bbab1a3cd9f7ba763a0a503b1911c1` | Historical rendering-failure record; references an absent qa/sample.docx. |
| `start-service.ps1` | 788 | `772bda666ef5f36b8ef01502b421000d809e08f88b94b690103534c681b5e3bd` | Foreground service launcher using the project-local virtual environment. |
| `STATUS.md` | 3885 | `0badc65f5f1598e4c0bf631c511157431b92c6027b7cb1dd1b7aa6d2ea12908c` | Historical implementation and validation claims, source inventory, and acceptance boundaries. |
| `src/docstream/__init__.py` | 78 | `efa3ba4e72da57612f70aee2513a80d0e47dc41367dc60884ed5e5529e8bc241` | Package description and runtime version constant 0.1.0. |
| `src/docstream/__main__.py` | 49 | `76fa916e93e0ae1a6c1bb51dcc0bcf289c014e9f760a47165f8a84401ccf41d7` | Python module entry point invoking cli.main and propagating its exit status. |
| `src/docstream/cli.py` | 5761 | `321835c8a0381b2f2a8b2a5909b94f0564c1d63d4816bdb170ccccea3ae5839f` | Argument parser, six subcommands, output formatting, dispatch, DocumentError handling. |
| `src/docstream/conversion.py` | 13672 | `fc52e440dfa1d976346f9586c4ecd9cbc9f57ade7b46b336b27ebb008bc5a875` | Backend selection, conversion orchestration, native Markdown/DOCX conversion, conversion results. |
| `src/docstream/core.py` | 6705 | `99c14526d4a633fa7a25515e0be70c81f4a9b0ab59e55eac13e985e1c4f83ade` | Document errors, edit results, hashes, atomic text writes, audit append, creation/edit/inspection. |
| `src/docstream/service.py` | 6029 | `4d7deda101a5bfd76248018441e69380a5155f8e496e09a6484f2c32de5828ff` | Root resolution, operation dispatch, HTTP handling, mutation lock, server lifecycle. |
| `tests/test_docstream.py` | 5469 | `d65ba22cc5d6f4e3d40b3aec5f8327ddd63cf8b50b952eb0ec411b928cfceec7` | Seven unittest methods, sample Markdown, temporary directories, live HTTP test source. |

## Component relationships

The console entry point is `docstream.cli:main` (pyproject.toml:15–16). Python module invocation reaches the same function through __main__.py:1–3. CLI dispatch calls core operations, conversion operations, or run_server (cli.py:86–139).

HTTP requests flow from ThreadingHTTPServer through make_handler to DocumentService.execute (service.py:31–143). That dispatcher calls the same core and conversion functions. DocumentService supplies a root resolver and an instance-local mutation lock; the CLI calls the underlying functions directly without that lock.

Conversion orchestration selects either an external executable or the native helpers (conversion.py:32–140). The native helpers import python-docx lazily (143–153, 160–200, 241–369). Core provides file hashing, text replacement, text writes, inspection, and audit append. There is no database, plugin framework, GUI, frontend, background queue, migration system, or document model separate from Markdown text in the supplied archive.

## CLI surface

| Command | Inputs/options declared in source | Implementation |
| --- | --- | --- |
| Global | `--version`; required subcommand | cli.py:30–36 |
| `new` | path, required `--title`, `--force`, `--json` | cli.py:38–42; core.py:165–178 |
| `inspect` | path, `--json` | cli.py:44–46; core.py:181–218 |
| `edit` | path, required `--pattern`, `--replacement`, `--flags`, `--expected`, `--limit`, `--dry-run`, `--backup`, `--json` | cli.py:48–57; core.py:97–162 |
| `import` | source, required output, backend, Pandoc executable, force, JSON | cli.py:59–65; conversion.py:59–95 |
| `publish` | source, required output, backend, Pandoc executable, reference DOCX, force, JSON | cli.py:67–74; conversion.py:98–140 |
| `serve` | required root, host default 127.0.0.1, port default 8765, backend, Pandoc executable | cli.py:76–82; service.py:127–143 |

No CLI audit-path option is exposed. No restore, history-query, document-listing, batch, template-management, or GUI commands are defined. Absence is a catalog observation, not a requirement that these features be added.

## HTTP surface

Source: service.py:31–80 and 83–124. Operation routes ignore URL query components. POST success responses wrap results as `{ok: true, result: ...}`. GET health returns its object directly. Required fields below are accessed by dictionary indexing; optional fields are not validated against a formal schema.

| Method/route | Required JSON fields | Optional JSON fields | Success |
| --- | --- | --- | --- |
| GET `/v1/health` | None | None | 200; ok, version, root |
| POST `/v1/health` | None | None | 200; wrapped health object; implemented but not advertised |
| POST `/v1/new` | path, title | force | 201; creation result |
| POST `/v1/inspect` | path | None | 200; inspection result |
| POST `/v1/edit` | path, pattern | replacement, flags, expected, limit, dry_run, backup | 200; edit result |
| POST `/v1/import` | source, output | backend, pandoc, force | 201; conversion result |
| POST `/v1/publish` | source, output | backend, pandoc, reference_doc, force | 201; conversion result |

GET unknown routes return 404. POST unknown routes raise DocumentError and return 400. Missing fields and selected validation exceptions return 400; other exceptions return 500 with exception text. The handler caps declared request length above 2 MiB but has no corresponding document-size cap, explicit read timeout, or nonnegative-length check.

## Data records and storage

| Record/storage | Fields or location | Source |
| --- | --- | --- |
| EditResult | path, replacements, changed, dry_run, before_sha256, after_sha256, backup, diff | core.py:24–36 |
| ConversionResult | source, output, backend, source_sha256, output_sha256, warnings | conversion.py:19–29 |
| Creation result | path, sha256, title | core.py:165–178 |
| Inspection result | path, sha256, bytes, lines, words, headings with line/level/text, links, images, code_blocks, unclosed_code_fence | core.py:181–218 |
| Default audit file | target parent/.docstream/audit.jsonl | core.py:74–83 |
| HTTP edit/import/publish audit | service root/.docstream/audit.jsonl | service.py:53,64,77 |
| HTTP new audit | new target parent/.docstream/audit.jsonl; not explicitly centralized | service.py:34–39; core.py:174–176 |
| Backup | source filename plus .bak; one reusable slot | core.py:135–137 |

Audits include UTC timestamps and operation-specific result objects. Edit audit records retain the pattern, flags, limit, expected count and result excluding the diff; replacement text is not recorded. No schema version, operation ID, actor identity, hash chain, immutable storage, or restore index is implemented.

## Dependency and distribution catalog

- Distribution name: docstream-cli; version 0.1.0. Runtime version is separately declared as 0.1.0. Python requirement: >=3.10. Source: pyproject.toml:5–13; __init__.py:3.
- Build backend: setuptools.build_meta; build requirement setuptools>=68; src package discovery. Source: pyproject.toml:1–3,18–19.
- Declared runtime dependency: python-docx>=1.2,<2. It is required by packaging even for Pandoc-only use. Third-party packages are not physically bundled in this ZIP.
- Optional external executable: Pandoc, selected through PATH or an explicit path/name. No pinned executable version or runtime version check exists.
- Core, CLI, service and tests otherwise use Python standard-library modules. Native conversion uses python-docx, including internal OOXML helpers for shading.
- install.ps1 creates .venv, upgrades pip, installs this project, and invokes the installed command's version. start-service.ps1 runs in the foreground and requires an already resolvable document root.
- LICENSE contains MIT text and a year, with no copyright-holder name. This is a documentation observation, not a legal determination.

## Existing test catalog

All tests live in tests/test_docstream.py and use unittest. No tests were executed during this assessment.

| Test method | Lines | What its assertions actually inspect |
| --- | --- | --- |
| test_new_inspect_and_guarded_edit | 41–65 | Creation title, dry-run replacement count and unchanged source, changed flag, backup existence, first inspected heading |
| test_inspect_ignores_headings_inside_code_fences | 67–73 | Heading exclusion in a triple-backtick fence, code-block count, closed-fence flag |
| test_match_guard_prevents_write | 75–80 | Error and unchanged text when two replacements conflict with expected=1 |
| test_capture_replacement_and_newline | 82–92 | Capture substitution count and resulting LF text |
| test_native_round_trip | 94–107 | Backend names, DOCX size, recovered title/status/table-header substrings |
| test_service_root_containment | 109–115 | Rejection of a Windows-style parent traversal and health result |
| test_http_edit_endpoint | 117–147 | One HTTP edit, success flag, replacement count, resulting file text |

The round-trip test does not assert exact equality, heading levels, inline formatting, list depth, rendered layout, or byte preservation. The suite contains no explicit audit-content assertion, Pandoc-path test, CLI subprocess test, atomic-failure test, concurrent-writer test, symlink test, or resource-limit test.

## Referenced material absent from this archive

STATUS.md:12–13 references a release SHA-256 manifest; none is included. STATUS.md:49 reports a built wheel; no wheel is included. render-failure.txt:3 references qa/sample.docx; no qa directory or sample DOCX is included. STATUS.md:11 references an earlier conversation that is not supplied in the archive. Claimed build-environment dependencies and renderer observations are not current-host measurements.

There is no separate requirements report, mining/standardization report, lockfile, CI configuration, OpenAPI document, changelog, or release-automation configuration in the supplied entries. Their absence is not proof they never existed elsewhere.

## Workspace boundary

Before this approved review, the workspace held the previously created AGENTS.md. The two review outputs are separate from the source archive and are not part of its v0.1.0 inventory. No original file was extracted, installed, or rewritten. See PROJECT_ASSESSMENT.md for findings, evidence limits, and proposed next decisions.