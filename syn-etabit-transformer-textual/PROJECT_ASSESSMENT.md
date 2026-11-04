# Docstream 0.1.0 — Complete static project assessment

Date: 2026-10-28 (America/New_York).

## Assessment conclusion

Docstream is a compact, inspectable implementation of a Markdown-first document workflow, with a shared core behind a CLI and an HTTP service. It is a useful development baseline. The reviewed source does **not** establish a production-ready document service, a preservation-grade editor, or a high-fidelity Word round-trip system.

The most consequential source findings are request-controlled executable selection, incomplete containment of derived write paths, inconsistent byte/provenance semantics, and nontransactional conversion/audit writes. Native conversion is intentionally limited, but some losses extend beyond the README's explicit limitations. Seven existing tests provide examples of the intended workflow; they do not substantiate all the verification claims in STATUS.md.

This judgment concerns the supplied implementation and evidence. The user's final product requirements remain unresolved; feature absence alone is not a defect.

## Authorization, sources, and method

The user approved the specific static catalog-and-assessment proposal by replying "yes". Approved outputs are PROJECT_CATALOG.md and PROJECT_ASSESSMENT.md in <source-workspace>. The governing production gate and project AGENTS.md apply. Implementation, code execution, installation, service launch, fixes, release work, and extraction were not approved and were not performed.

Source: <local-user-home>\Desktop\Inbox\docstream-0.1.0.zip

Reviewed archive SHA-256: `4acbdb5ee634ede3067fa2ad7c189afbd051365e6714b72ad03159fd4df8bf72`.

All 15 entries were enumerated, each entry's uncompressed bytes were hashed, and all 14 regular files were read directly from the ZIP. PROJECT_CATALOG.md supplies the exhaustive inventory, component map, command/API surfaces, result records, and test catalog. No project module, test, PowerShell installer, or external converter was executed. No external documentation research or dependency-version investigation was performed; conclusions below are based on the supplied source.

Locators use archive-relative paths and one-based source line numbers, excluding the prefix docstream-0.1.0/. They refer to the reviewed archived bytes, not extracted workspace files. Source is decoded as text for line references; hashes use original bytes.

Evidence labels:

- **Observed source:** a control flow, declaration, or absence visible in the reviewed files.
- **Static inference:** a consequence derived from that source; not a runtime reproduction.
- **Source-reported:** a historical assertion in supplied documentation, not independently verified here.
- **Unknown:** unavailable evidence or a product decision not supplied.

Priority indicates proposed remediation order: P1 for execution authority or material data-integrity risks; P2 for significant correctness/reliability gaps; P3 for clarity and maintainability. Priorities are assessment judgments, not user-approved implementation tasks.

## Architecture and strengths worth retaining

The architecture separates argument handling (cli.py), shared file operations (core.py), conversion (conversion.py), and HTTP transport (service.py). That separation makes the system understandable and gives CLI and service users a common operation layer. The package contains six Python modules, one test module, two Windows helper scripts, package metadata, license text, and three explanatory/status files.

Useful mechanisms visible in source include:

- Shared result dataclasses with JSON serialization (core.py:24–36; conversion.py:19–29).
- Pre-write replacement-count checks and dry-run diffs (core.py:119–138).
- Same-directory temporary text files, file fsync, replacement, and cleanup (core.py:55–71). This is a meaningful text-write safeguard, with limits discussed below.
- Resolved-path root membership checks for primary HTTP paths (service.py:23–29).
- Instance-local serialization of HTTP mutations (service.py:21,35,43,57,69).
- Explicit converter selection and user-facing backend failures (conversion.py:32–56).
- A localhost default, structured JSON responses, and a declared request-body cap (service.py:87–119; cli.py:79).
- Documentation that distinguishes structural DOCX success from visual page-layout validation (README.md:105–107; STATUS.md:31–50).

These are source observations. Their behavior has not been exercised during this review.

## Findings register

### F-01 — P1 — HTTP clients can select a host executable

**Evidence:** service.py:61–62,73–74 passes request fields backend and pandoc into conversion. conversion.py:32–40 accepts any existing file or executable found by shutil.which as the Pandoc path. conversion.py:75–79,117–123 invokes that executable with subprocess.run. No executable allowlist, authentication, or per-request authorization is implemented.

**Trigger and implication:** a caller who can reach an import/publish endpoint and supply an existing source can choose a host executable instead of the administrator-configured Pandoc. The executable is launched under the service process identity with conversion-shaped arguments. Root resolution is not applied to this executable field. This grants executable-selection authority beyond document-path access.

**Limit:** this is not a demonstrated shell-injection finding: subprocess.run receives an argument list and does not set shell=True. Arbitrary payload behavior depends on the chosen executable and its argument interpretation. No exploit was attempted.

**Proposed disposition:** make executable configuration a trusted startup setting, reject executable overrides in document requests, define the local caller trust model, and validate executable identity/version under an approved policy.

### F-02 — P1 — Derived writes are outside the complete containment check

**Evidence:** service.py:23–29 resolves the main path under root. core.py:135–137 derives a .bak path and writes through shutil.copy2 without resolving or checking that derived destination. core.py:74–83 opens a derived audit path normally. Service audit paths at service.py:53,64,77 are constructed under root but not passed through resolve; new uses its target-parent audit path (core.py:174–176).

**Trigger and implication:** if an existing .bak file or .docstream directory is a symlink/reparse-point alias to a location outside the root, the derived write may reach outside it even though the primary document passes containment. This requires filesystem conditions and permissions that were not probed. It is a static containment gap, not a reproduced escape.

A separate check/use race exists between resolving a path and later opening it if another process can change directory links or entries. The service's in-process lock does not prevent outside filesystem changes.

**Proposed disposition:** include backups, logs, temporary files, reference documents, and conversion artifacts in the filesystem policy; reserve internal storage paths; define symlink/reparse-point handling and supported threat assumptions. Validate with platform-specific cases after approval.

### F-03 — P1 — Editing changes newline bytes and mislabels the pre-edit byte identity

**Evidence:** core.py:113 reads via Path.read_text, which uses universal-newline text decoding. Lines 114 and 145 hash UTF-8 encodings of the decoded strings. atomic_write_text writes with newline="" (61). inspect_markdown reports the raw file digest through file_sha256 (209), which is a different representation.

**Trigger and implication:** with a CRLF source, decoded text contains LF. An actual edit rewrites the entire document with LF, including untouched lines. before_sha256 then represents normalized text bytes rather than the original file bytes. A no-change result can also report a digest different from the file's byte digest. This undermines exact provenance and produces changes beyond the requested textual substitution.

**Proposed disposition:** explicitly separate byte hashes from decoded/normalized text hashes; decide newline, BOM, and encoding policies; preserve byte conventions where promised. The existing LF-only capture test cannot detect this issue.

### F-04 — P1 — Conversion does not consistently protect existing outputs

**Evidence:** conversion.py:76–79,118–123 gives the final output path directly to an external converter. Native publish saves directly to the final output at 368. Native import alone uses atomic_write_text (82). Existence checks occur earlier at 70–71 and 110–111.

**Trigger and implication:** publishing with force or a failing/interrupted converter can damage or leave incomplete final output. Without force, another writer can create a destination between the check and the final write. There is no rollback or conversion-stage verification before final replacement. Same-directory atomic text writes in core do not cover these other paths.

**Proposed disposition:** define overwrite and recovery policy, write conversions to a controlled staging file, verify the result, and commit with the approved collision/concurrency semantics.

### F-05 — P1 — A completed mutation can be reported as failure after audit append fails

**Evidence:** edits write at core.py:138 and append audit at 149–161. Creation writes at 172 and audits at 174–177. Import/publish produce output before audit append at conversion.py:91–94,136–139. Errors propagate after the document mutation, without transaction state or rollback. HTTP maps unexpected exceptions to 500 (service.py:118–119).

**Trigger and implication:** if audit storage is unwritable or full, the file may already be changed while the caller receives failure. A retry may repeat the mutation. No idempotency key, transaction ID, or explicit committed-but-audit-failed result exists.

**Proposed disposition:** agree whether durable audit is mandatory, define recoverable operation states, and report partial completion accurately. Do not claim append plus file replacement forms a transaction.

### F-06 — P2 — Resource limits do not bound document work

**Evidence:** regex patterns are length-limited but run through ordinary re.subn without a timeout (core.py:111–119). Files and full diffs are held in memory (113,125–132). Pandoc processes have no timeout and capture all output (conversion.py:77,121). HTTP caps Content-Length above 2 MiB but has no nonnegative check or explicit body-read timeout (service.py:105–109). Mutations hold a single service-wide lock.

**Trigger and implication:** pathological regular expressions, very large documents, negative declared lengths, slow bodies, or hung converters can consume resources or stall mutation progress. A short pattern is not necessarily bounded in evaluation time. Negative lengths are passed directly into read; resulting read/blocking behavior has not been tested here.

**Proposed disposition:** define size, duration, queue/concurrency, and response limits, then choose mechanisms that actually enforce them. Assess DOCX archive expansion limits separately if untrusted documents are in scope.

### F-07 — P2 — HTTP coercions can turn malformed fields into destructive options

**Evidence:** service.py:37,51–52,63,76 uses bool(value). The string "false" therefore becomes true for force, dry_run, or backup. limit is converted by int (50), allowing coercions rather than a strict integer schema. expected, title, pattern, flags, and paths lack field-type validation. Unknown fields are ignored.

**Trigger and implication:** a caller sending force as the string "false" can enable overwrite. Wrong types can produce 500 responses instead of a field-specific client error. This is an API contract defect even if well-behaved JSON callers normally send booleans.

**Proposed disposition:** specify and validate exact input types, integer ranges, required/unknown fields, and consistent error envelopes before dispatch.

### F-08 — P2 — Replacement-count and limit semantics differ from the README

**Evidence:** core.py:119 obtains count from subn after applying count=max(0, limit). Lines 120–123 compare expected to replacements performed. README.md:62 says exactly N matches must be found. Negative limits become zero, meaning unlimited replacement.

**Illustrative static case:** with text "one one", pattern "one", replacement "two", limit=1, expected=1, the code permits a write even though there are two available matches. The guard counts selected substitutions, not all matches. This example is reasoned from source and was not run.

**Proposed disposition:** decide whether expected means total matches or applied replacements; make that explicit in CLI/API/docs and reject negative limits. Keep the current semantics only if deliberately accepted.

### F-09 — P2 — Concurrent writers can overwrite one another; backups retain one slot

**Evidence:** service.py has one RLock per DocumentService instance. core.py:113–138 has no file lock or expected-current-hash check. append_audit has only a process-local threading lock (17,77–79). Backup names are always the same .bak path (136).

**Implication:** CLI processes, multiple service instances, and outside editors are not coordinated. Two edits can read the same original and replace one another's changes. Repeated backup-enabled edits overwrite the prior backup. Atomic file replacement prevents some partial-file states, not lost updates or multi-file transaction failure. Metadata preservation of rewritten files is not explicitly implemented.

**Proposed disposition:** decide supported concurrency and history retention; use optimistic version checks and/or file coordination appropriate to that decision, with recoverable versioned backups if required.

### F-10 — P2 — Source/output aliases can destroy the source and misstate provenance

**Evidence:** import_docx and publish_docx have no source/output identity or hard-link alias check (conversion.py:59–140), accept force, and compute source_sha256 only after output generation (87,132). No extension contract is enforced.

**Trigger and implication:** if output aliases source and overwrite is enabled, conversion can replace the source. Native publishing reads the Markdown before saving DOCX, then hashes the now-overwritten source; the reported source digest no longer identifies the original Markdown. Other backend outcomes depend on converter behavior. File extensions do not prevent the operation in this code.

**Proposed disposition:** reject source/output/reference aliases as required, define accepted formats, and capture source identity before conversion with a stable-source policy.

### F-11 — P2 — Native import drops inline semantics and shifts heading levels

**Evidence:** conversion.py:182–198 uses block.text and style, not run formatting or hyperlink relationships. It emits the first Title as #, and any Heading N as min(6,N+1) hashes (186–192). Native export treats the first # as Title but emits subsequent heading levels directly (323–332).

**Implication:** bold, italic, inline code distinctions, and hyperlink target relationships are not reconstructed by native import. An imported Word Heading 1 becomes Markdown ## even when there was no Title. Repeated publish/import cycles can shift headings; a sample ## exported as Heading 2 returns as ###. The existing round-trip test checks the title and selected substrings, not heading-level or formatting preservation.

**Proposed disposition:** define title-versus-heading semantics and a directional fidelity contract. Preserve supported semantics or generate precise loss warnings. Byte-perfect Word round-tripping is explicitly not promised by STATUS.md:5.

### F-12 — P2 — Native lists, tables, and Markdown handling are a limited dialect

**Evidence:** import recognizes list styles by name and emits flat markers (conversion.py:193–196); export matches indentation but discards it and explicit numbering (335–342). Table import takes cell.text, treats the first row as a header, and escapes only backslashes and pipes (156–180). Inline rendering is one regex (203–226); fences toggle on lines starting with triple backticks (283–299).

**Implication:** nested-list hierarchy, starting numbers, numbering definitions, merged/nested table structure, and table-cell paragraph boundaries are not preserved. Newlines inside cell text are not encoded for pipe-table rows. Markdown-special characters from Word prose can acquire new meaning after import. Images, raw HTML, reference links, nested emphasis, tilde fences, and many other syntax forms are not implemented as structured features. Image syntax can be partly consumed as a link while leaving its leading exclamation mark.

These are limitations of the implemented dialect, not evidence that a particular external Markdown standard was promised. The generic warning does not enumerate document-specific losses.

**Proposed disposition:** agree a supported syntax/features matrix and loss policy. Then decide whether to retain the custom parser, constrain input, or use an established parsing representation. Do not choose that architecture before requirements are agreed.

### F-13 — P2 — Backend selection and Pandoc reporting have correctness gaps

**Evidence:** conversion.py:45 resolves an explicit Pandoc argument before honoring requested=native (52–53). Thus an invalid explicit executable can fail a native-only operation. Successful subprocess stderr is discarded (77–79,121–123); warnings stays empty for successful Pandoc runs. Import does not request media extraction (76), publish declares GFM input (118), and the supplied command has no explicit citation-processing configuration.

**Implication:** backend results can vary by installed PATH tools, native operation unnecessarily depends on explicit Pandoc resolution, and successful converter warnings never reach ConversionResult. README.md:57 recommends Pandoc for media/citations, but the wrapper alone does not establish an end-to-end resource-preservation or citation workflow.

**Limit:** no Pandoc version, actual external converter behavior, or media example was tested. This review does not assert that Pandoc itself lacks these capabilities.

**Proposed disposition:** separate backend-specific validation, retain meaningful converter warnings, define resource/template handling and supported invocation policy, and record converter identity/version where required.

### F-14 — P2 — Audit storage is mutable, inconsistent, and not sufficient for replay

**Evidence:** core.py:74–83 appends plain JSONL with no durability flush, hash chain, actor, operation ID, or schema version. Edit audit omits replacement text and diff (153–159). HTTP new uses target-relative storage while other HTTP mutations use service-root storage. The path resolver permits operations on .docstream/audit.jsonl itself because it has no reserved-path exclusions.

**Implication:** logs can be modified by ordinary authorized file operations; they are neither immutable nor independently attested. They record useful observations but cannot fully reconstruct edits without additional history. Searching for one service history can miss new-document events in subdirectories. A no-change non-dry edit is logged too (149), whereas dry runs are not logged.

**Proposed disposition:** agree whether the requirement is lightweight operational logging, complete recoverable history, or stronger evidence preservation. Design storage and permissions to that actual requirement; do not imply append-only code confers tamper resistance.

### F-15 — P2 — Network and error handling boundaries are permissive

**Evidence:** cli.py:79 accepts any host, and start-service.ps1:6,23 forwards any BindAddress. service.py implements no authentication, TLS, Host/Origin validation, or JSON Content-Type enforcement. Health returns the absolute root (33). Unexpected errors include exception text (119). CLI catches only DocumentError (cli.py:134–139); IO errors, some conversion errors, Unicode errors, and invalid replacement expressions may escape as tracebacks.

**Implication:** localhost is a default, not an enforced bind restriction or caller authorization boundary. A configured network bind exposes the same unauthenticated operations. Browser-origin protections and local multi-process access have not been established; no browser exploit is claimed. Error responses may disclose filesystem details and do not consistently distinguish expected client failures from internal problems.

**Proposed disposition:** settle the caller/deployment model before choosing authentication and binding policy, normalize operational errors, and document failure and HTTP status contracts. Network service operation is not approved by this review.

### F-16 — P2 — Existing evidence is narrower than the status report

**Evidence:** tests/test_docstream.py contains seven methods. STATUS.md:24–26 describes flags, limits, recoverability, and provenance as verified. The supplied tests do not explicitly test nondefault flag handling, limits, audit contents, digest identity, forced-overwrite recovery, or failure atomicity. The native round-trip test uses three recovered-text substring checks (105–107). STATUS.md:45–49 reports historical successful tests, CLI smoke checks, structure checks, and a wheel build without the corresponding logs/artifacts.

**Implication:** the archive includes test source but not independently reproducible evidence of all reported claims. Prior checks might have existed elsewhere; their absence here does not prove they were never performed. The current review has not rerun any checks.

**Proposed disposition:** reconcile claims with specific tests and retained evidence, then execute an approved bounded runtime plan. Keep source-reported status distinct from current verification.

### F-17 — P3 — Installation and release metadata need strengthening

**Evidence:** install.ps1:12,15–20 invokes native programs without explicit LASTEXITCODE checks; ErrorActionPreference alone does not establish consistent fail-fast native-command behavior across PowerShell configurations. The script prints "Installed" before the final version invocation. pyproject.toml leaves build/runtime versions ranged and names its author "Generated for local use". Version 0.1.0 is duplicated in metadata and __init__.py. LICENSE:3 lacks a holder name.

**Implication:** failure reporting and reproducibility are underspecified. No lockfile, CI workflow, installed-command test configuration, wheel artifact, or release manifest is included. STATUS.md:15's "Bundled dependency" describes a prior environment; this ZIP declares python-docx rather than carrying its distribution. No current dependency vulnerability audit or legal provenance determination was performed.

**Proposed disposition:** check native exit codes, define install/update behavior and supported versions, establish reproducible validation/release evidence, and have the user supply authoritative attribution details where needed.

### F-18 — P3 — Inspection metrics and the README sample need clarification

**Evidence:** core.py:191–205 recognizes only selected ATX headings, inline links/images and triple-backtick fence toggles. Word counting includes the full source (206), while heading/link inspection skips recognized fenced content. CLI new writes only a heading (core.py:171). README.md:29–41 then immediately tries to replace a Status: Draft line with expected=1 without inserting that line.

**Implication:** inspection is a heuristic summary, not comprehensive Markdown validation; inline code and alternative syntax can produce misleading counts. Following the README's new-document example literally reaches a match-count failure. The containment test uses a Windows separator (tests/test_docstream.py:112), which is not a traversal separator on POSIX, limiting its portability as a test.

**Proposed disposition:** document metric definitions and dialect limits, correct the sample workflow, and align platform tests with the supported operating systems.

## Document fidelity matrix

This matrix describes source-supported native behavior, not verified render output.

| Feature | Markdown to DOCX, native | DOCX to Markdown, native |
| --- | --- | --- |
| Title/headings | First # becomes Title; later headings use same numeric Word heading | First Title becomes #; Word Heading N becomes N+1, capped at 6 |
| Paragraphs | Adjacent nonblank prose lines joined by spaces | Nonempty paragraph text, stripped; blank paragraphs omitted |
| Bold/italic/code | Simple inline regex produces formatted runs | Run formatting not reconstructed |
| Hyperlinks | Visible label plus target text; not constructed as hyperlink relationship | Paragraph text only; target relationships not explicitly serialized |
| Lists | Flat bullet/number styles; depth and start numbers discarded | Selected style-name recognition; flat markers |
| Tables | Simple pipe syntax, grid style, shaded first row | cell.text, first row forced to header, simple escaping |
| Blockquotes | Indented italic text for > prefix | No quote-style mapping |
| Code blocks | Triple-backtick toggle, monospaced output | No code-style mapping back to fences |
| Images/media | No image insertion implementation | No media extraction implementation |
| Templates/layout | Fixed Letter page, fixed margins/fonts; reference DOCX ignored with warning | Layout and reference style semantics not preserved |
| Word-specific features | No implementation for comments, revisions, fields, footnotes, headers/footers | Main-body text/table traversal; no dedicated preservation path |

Pandoc is a separate backend whose actual fidelity remains unknown here. No renderer or Word/PDF visual inspection was used. Neither a valid DOCX container nor recovered text substrings establish layout fidelity.

## Claim reconciliation and missing evidence

| Supplied statement | Current assessment |
| --- | --- |
| Seven tests passed (STATUS.md:45) | Seven test methods are present; result is historical and not rerun. |
| Live HTTP and CLI smoke checks passed (46–47) | One HTTP edit test is present; no CLI smoke transcript is supplied. |
| DOCX structural validation passed (48) | Historical report only; no sample DOCX or retained structure-check output is supplied. |
| Wheel built (49) | Historical report only; wheel and build log absent. |
| Visual render blocked (36,50; render-failure.txt) | Supplied failure record says missing soffice.exe on 2026-10-27; not a current-host capability check. |
| Release manifest identifies source/tests (12–13) | Referenced manifest absent; this review creates its own entry digests in PROJECT_CATALOG.md without reconstructing the missing original. |
| Native deterministic standard conversion (README.md:55) | Explicit backend avoids auto-selection drift; byte-for-byte deterministic DOCX output has not been demonstrated. |
| Root-scoped service (README.md:71) | Primary path check exists; executable configuration and derived writes have wider boundaries. |
| Atomic writes/recoverability | Text writes have an atomic-replacement mechanism; conversion paths, audit transactions, concurrent writers, and history retention have the limits described above. |

## Product decisions required before development

The current request to develop the project fully does not settle these choices. The assessment makes no silent selections:

1. Intended users and interfaces: personal CLI, local AI agents, desktop UI, integration service, or distributable product?
2. Document authority: Markdown as master, Word as master, or an explicitly mapped dual-format workflow?
3. Required fidelity: exact wording, Markdown structure, inline semantics, media, templates, tracked changes, or page layout? Which losses must block output?
4. Trust boundary: only a trusted operator, multiple local processes/users, browser access, or network callers? Are input documents untrusted?
5. Recovery and provenance: optional single backup, version history, transactional audit, recoverable operation journal, or stronger evidence preservation?
6. Supported operating systems, Python versions, converter dependencies, install location, and upgrade model?
7. Workload: expected document size, concurrency, batch operation needs, and latency limits?
8. Governing source: is there an earlier requirements/design conversation or report whose requirements supersede the generated README?

## Proposed development sequence — not approved implementation

| Stage | Proposed outcome | Dependencies and later acceptance evidence |
| --- | --- | --- |
| 1. Product contract | Agreed users, document authority, fidelity matrix, trust/recovery policy, supported platforms | User answers and a scoped approved implementation proposal |
| 2. File and execution boundaries | Trusted converter configuration, strict inputs, safe path/alias policy, defined write commits | Bounded negative cases for executable overrides, derived paths, malformed fields, aliases |
| 3. Integrity and operation outcomes | Correct byte hashes, declared encoding/newline policy, stable source checks, conflict detection, truthful partial failures | Representative CRLF/LF/BOM files, competing writers, backup/audit and commit failures |
| 4. Conversion contract | Chosen title/heading mapping, explicit supported syntax, loss diagnostics, resource/template behavior | Directional semantic fixtures plus representative documents; no assumption that all Word features are required |
| 5. Interfaces and service lifecycle | Consistent errors, access policy, limits, cancellation/timeouts where required | Approved CLI/API tests for failure and success paths under the selected deployment model |
| 6. Release readiness | Reliable installer, dependency/build policy, accurate docs, release inventory and provenance | Clean supported-machine install/build evidence; visual document review if required by acceptance criteria |

A GUI, database, cloud service, larger framework, or new parser is not assumed. The selected requirements should determine those choices. No runtime test plan, dependency installation, or remediation stage is authorized by this assessment approval.

## Bounded validation performed and completion boundary

- Enumerated every archive entry and hashed every uncompressed payload; catalog includes all 15 entries and all 14 regular files.
- Read every supplied implementation, script, metadata, license, test, and documentation file.
- Cross-referenced the six CLI commands, five advertised POST operation endpoints, additional implemented POST health route, GET health route, result schemas, audit destinations, and seven test methods.
- Compared documentation and status claims against the supplied source and test assertions; retained missing artifacts as gaps.
- Attached source locators, triggers, consequences, and proof limits to findings; illustrative behavior was not represented as runtime reproduction.
- Produced only the two approved report files. The source archive remains the original baseline. No source was extracted or changed, and no project behavior was executed.

Completion applies to this static catalog and assessment only. Runtime reliability, converter availability/fidelity, visual output, installability, and final product acceptance remain unverified or undecided. Any implementation or runtime validation requires a separate concrete scope and user approval under the standing gate.