# M3 rendering implementation and validation

Date: 2026-10-29 (America/New_York).

## Authorized scope and result

The user explicitly approved project-local Playwright/Chromium, a managed
renderer, preview/artifact tools, rendered commit, versioned cache/publication
records and bounded visual/integration testing. M3 is complete for that scope.

**80 tests passed, zero failures, zero errors.** The prior 66 service/CPU tests
remain in the suite, including 420 fixed-seed generated transformation cases.
Fourteen rendering/migration/network tests exercise actual browser output and
publication/commit boundaries. Method outcomes and actual timing are in
m3-test-output.txt and m3-test-results.json. This is correctness evidence, not
a performance benchmark or unrestricted production-readiness claim.

## Installed rendering environment

Python 3.12.14, SQLite 3.53.1, Playwright 1.64.1 and Chromium 156.0.8078.4,
revision 1248. Browser components are in service/.browsers, not a global browser
installation. The Playwright install also downloaded its matching headless shell,
FFmpeg and Windows helper. The renderer selects the pinned Chromium executable.

Registered font files provide Arial, Times New Roman and Consolas with normal,
bold, italic and bold-italic faces. Renderer metadata records file identities and
actual custom-font usage. An unavailable requested font fails explicitly.

The editable package is version 0.2.0.dev3. Resolved versions and renderer/browser
identities are retained separately. No Codex client registration, automatic-start
task, firewall change or GPU backend was created.

## Actual observed cases

| Case | Result |
| --- | --- |
| First preview | Semantic result constructs and publishes actual PNG/PDF. |
| Same content/profile under a new request | Cache hit, no additional browser render. |
| Profile margin change | New cache key and actual render. |
| Changed content | Warm worker reused. |
| Four font changes returning to original | Four logical outputs, zero reduced writes, existing rendering reused. |
| Missing font | FONT_UNAVAILABLE; original document head unchanged. |
| Artifact bytes damaged | Integrity failure; new request regenerates, damaged bytes quarantined. |
| Files published before metadata failure | No ready artifact records or head advance; orphan files remain unadvertised. |
| Failure before final head/receipt commit | Head unchanged; ready cache reusable on a new request. |
| Store restart | Receipts and cache reused without another render. |
| Long PDF | Multiple pages and final paragraph text present. |
| HTML-like source text | Escaped; no document-provided script executed. |
| v1 migration | Existing semantic content preserved; backup remains v1; migrated store passes integrity_check. |
| Real MCP render/retrieve | Structured tool results and authenticated PNG download succeed. |
| Missing download authentication | Request rejected. |
| ASGI shutdown | Worker is closed before shutdown acknowledgement; fixture confirms no worker object remains. |
| Actual renderer limit failure | Head unchanged; a later valid request succeeds. |
| Dead worker | Next uncached result replaces the worker and renders successfully. |

## Representative visual review

The maintained examples/render_example.py produced an actual service example in
.docstream/visual-example. M3_EXAMPLE.json records its original preview, candidate,
rendered commit and artifact locations. It records one worker start, one actual
render, four logical outputs, zero reduced writes, and a cache hit for the final
rendered commit. Both PNG and PDF are content-addressed managed artifacts.

The PNG was inspected directly. The one-page PDF was rendered through the bundled
Poppler pdftoppm at 110 DPI and the page image inspected. Title, heading hierarchy,
paragraphs, bold/italic blocks, bullets, code panel and page margins are legible;
no visible overlap, clipped content or missing text was observed. The QA page is
retained in docs/m3-qa. Multi-page fixture PDFs were text/structure tested and are
not represented as individually visually reviewed deliverables.

This review validates the service's layout on this host. It is not Word-layout
certification, multilingual coverage proof or independent attestation.

## Corrections and retained earlier evidence

The first example attempt failed before browser launch because the installed
Windows job API required a string object name. A unique owned job name corrected
that call; the failed durable receipt is retained in the example store. A new
request key was used, preserving the original failure record.

The first combined run had one genuine lifecycle failure: the renderer could
remain after the ASGI app acknowledged shutdown. Its log is retained in
m3-initial-combined-run.txt. Cleanup now runs in a shielded section before the
shutdown acknowledgement. The final suite passes the worker lifecycle check.

## Remaining boundaries

Only the existing structured text/style subset is rendered. Tables, images,
Markdown/DOCX adapters, inline spans and Word-specific features remain later work.
The default inherited Aptos font is not available in the explicit registry and
is never silently replaced. Callers select a registered family intentionally.

Cache identities describe pinned renderer/font inputs captured by this process;
runtime binary or registry changes require restart/revalidation. Staging/ready
publication is not a distributed transaction or OS filesystem sandbox. An account
owner can alter managed files; integrity checks refuse their use when inconsistent.

The renderer is bounded by dimensions, artifact size and parent wait budget. The
entire service is not a hostile-input resource-isolation proof. No GPU acceleration,
selective bypass, actual Codex UI registration, global startup or final release
acceptance is claimed. All test listeners and browser workers are stopped.
