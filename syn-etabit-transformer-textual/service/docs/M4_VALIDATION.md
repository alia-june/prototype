# M4a implementation and validation

Subsequent evidence notice, 2026-10-29: the separately approved three-mode
harness passes the prior regressions but adds 24 failed fuzzy cases in three
groups. See HARNESS_FINDINGS.md for NUL export classification, malformed
surrogate direct ingestion and CR/LF conversion policy. The historical 117-test
result below remains accurate for its declared fixtures; it is not broad product
acceptance. Product code was left unchanged by the harness scope.

Date: 2026-10-29. Version: docstream-cpu 0.2.0.dev4.

## Approved scope and result

The user approved the concrete M4a proposal with "yes approved". The scope is
complete: version-two content, Markdown/DOCX import and export, managed images,
explicit losses, service operations, compatibility and bounded validation.

**117 tests pass, zero failures, zero errors, zero skips.** This includes the
prior 80 CPU/service/rendering/baseline regression tests and 37 format/rich-model
tests. The prior suite includes 420 bounded generated cases; rich-model checks
add 80 fixed-seed generated assignment batches against the sequential reference.
Final execution evidence is in m4-test-results.json and m4-test-output.txt.
The final combined runner records roughly 44 seconds on this host. This is
correctness evidence, not a performance benchmark or production certification.

## Implemented and observed behavior

| Check | Observed result |
| --- | --- |
| Version-one serialization | Exact original JSON and digest retained, without added rich fields |
| Actual M3 store | A copied M3 SQLite store loads/recompiles plans; snapshot, stream, batch and document rows remain unchanged |
| Version-two content | Strict spans, heading levels, nested list metadata, rectangular cells and image references |
| Font reduction | Inline/table style cells conform to the sequential reference; exact restoration reduces to zero writes |
| Rich replacement | Complete block hash guard succeeds for the matching input and fails for a stale hash |
| Plain text replacement | Rich blocks reject a potentially destructive plain replacement |
| List editing | An operation cannot leave an orphaned intermediate list level |
| Markdown round trip | Supported fixture returns the same version-two semantic value and image bytes through the bundle |
| DOCX round trip | Supported text, heading/list structure, start values, inline formatting, cell order/header flags and image bytes/dimensions checked |
| Titles | Separate title metadata and level-three heading remain separate |
| Conversion losses | HTML, quote/code metadata, missing images, unsupported fonts/effects/placement, comments, tracked changes, merged cells and external relationships produce diagnostics |
| Markdown delimiter ambiguity | Export reparses its own output; changed supported meaning produces a loss diagnostic |
| Headerless table | An empty header is inserted only under accepted losses; first data is not promoted |
| Input packages | Unsafe/normalized/case-aliased names, expansion excess, invalid image data, and UTF-8/UTF-16 DTD/entity documents rejected |
| Persistence | Original source/image bytes survive restart; identical import/export keys replay durable receipts |
| Failed export publication | No ready artifact metadata or head advance; receipt remains failed and a new key can repair |
| Missing export artifact | Receipt preserved, ARTIFACT_UNAVAILABLE reported, new export key repairs it |
| Structure inspection | Explicit paths reach individual table-cell span text |
| Real network workflow | Official MCP client imports Markdown, exports DOCX and downloads authenticated bytes matching metadata |
| Download authentication | Missing bearer token rejected |
| Actual browser | Rich table/list/image fixture produces PNG/PDF and reuses ready artifacts |
| Font consistency | Rich code follows document inheritance; DOCX heading/code styles preserve that family choice |

Tests use controlled fixtures and bounded local stores/listeners. No user
document corpus was bulk processed. The original archive and 14 extracted
baseline files are rehashed separately in M4_SOURCE_VERIFICATION.json.

## Representative service and visual evidence

`examples/format_example.py` produced the retained final example under
`.docstream/m4-validation/example-0.2.0.dev4/`. M4_EXAMPLE.json contains its
source, both exports, transformation, preview, rendered commit and artifact
metadata. It records two logical font operations, zero necessary font writes,
one worker start and one actual browser render; rendered commit reuses the
preview. All calls are maintained application-service operations.

The direct preview was inspected. The final service PDF was rasterized through
bundled Poppler and its single page was inspected. The final DOCX was rendered
through the packaged render_docx.py using installed LibreOffice 26.8.0.3; its
single page was inspected. The heading hierarchy, nested numbering, inline bold/
italic/code/link, table, image and page boundaries were readable. No clipping,
overlap or missing fixture content was observed. The DOCX and service layouts
differ, as expected for distinct renderers and declared presentation defaults.
This is not Microsoft Word layout certification or an all-documents guarantee.

QA images/PDFs are retained under docs/m4-qa. Earlier example variants and
intermediate test logs remain available; they are not the final output baseline.
An initial table presentation was refined to light borders/header fill and
clear code-paragraph spacing before the final DOCX review.

## Retained failures and corrections

The first 29-test format run had one failed path assertion. Windows ZipInfo
normalizes backslashes both when constructing and reading entries. The test was
corrected to create an actual malicious entry, and package preflight now rejects
stored names changed by the ZIP reader. Initial and follow-up logs are retained.

A later input-limit assertion incorrectly expected schema rejection for a byte
count that shares the same base64 length as the valid boundary. It now verifies
both decoded-size rejection and the larger schema bound. A stricter style-loss
check also exposed an inherited Heading 3 spacing effect in the generated Word
template; the exporter removes unsupported font effects from its generated
heading/title styles. Final checks pass after these corrections.

Review also identified a presentation-only code font that could defeat an
all-text assignment. Version-two preview and DOCX output now honor semantic
font inheritance, with dedicated checks. Existing version-one behavior remains
compatible. No failed run is represented as successful evidence.

## Environment and remaining limits

Python 3.12.14, SQLite 3.53.1, markdown-it-py 4.2.0, python-docx 1.2.0,
Pillow 12.3.0 and lxml 6.1.1. The previously installed MCP/Playwright/browser
versions remain pinned. New local installations were markdown-it-py and mdurl;
the remaining format libraries already existed in the bundled runtime inherited
by the project venv. requirements-m3.lock preserves the earlier closure;
requirements-m4.lock and requirements-service.lock describe the current closure.
These are version pins without wheel hashes, not a standalone reproducible
installer or a complete supply-chain attestation.

Database schema remains 2; no migration or existing-store rewrite was needed.
Images reuse the existing sources table. The default managed store and the
original M3 example were not opened for mutation during M4a. Compatibility uses
a copied M3 store. Test/example stores live under the approved M4 validation
destination, apart from prior regression fixtures' existing validation folder.

The format contract declares loss policy, limits and unsupported features.
DOCX detection is conservative and does not exhaust the entire OOXML standard.
Complex styles/layout, exact Word pagination, merged/nested tables, floating
objects, tracked-change editing, macros and other advanced features remain
outside the supported semantic subset. Unsupported requested fonts still cause
explicit preview errors; no fallback alias was installed. Markdown bundle
metadata is necessary to retain document properties and image dimensions.

Agentic-control registration, credentials/control configuration, activation,
automatic startup, GPU execution, selective bypass and release/installer work
were not part of this implementation. Final integration remains last. All test
listeners and owned browser workers are stopped after validation; no ongoing
service was launched for production use.
