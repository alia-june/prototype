# Format hardening findings and remaining boundaries

Date: 2026-10-30. AUTH-15.

The three product findings below are corrected under the user's explicitly
approved policy. Their old failed runs, original inputs and source copies remain
intact. FORMAT_HARDENING_VALIDATION.md records the fresh run outcomes and limits.

## HF-01 — Corrected under the approved conversion policy

DOCX paragraph export formerly changed CR text into a line break that reimported
as LF, without reporting the change. It now reports `DOCX_CARRIAGE_RETURN` with
the affected output field location. The default service policy returns
`CONVERSION_LOSS` and publishes no artifact. Explicit allow produces output and
retains the diagnostic in its durable receipt, including after restart/replay.

The chosen mapping is one CR to one LF; existing LFs are retained. A CRLF pair
therefore produces two line breaks. Stored sources and streams keep their
original characters and hashes. A title uses the converted string consistently
in both its displayed paragraph and DOCX metadata. Paragraphs, inline runs,
table-cell paragraphs and version-one plain blocks are covered.

The harness's CR cases now explicitly declare the approved loss. The comparison
still verifies all remaining supported text, formatting and structure against
an independently adjusted expected value. A synthetic export with an unrelated
word change fails even when it reports the CR diagnostic. Missing diagnostics
also fail. This resolves a conversion-policy finding; it does not create global
newline equivalence or promise an exact CR-preserving DOCX representation.

## HF-02 — Corrected DOCX character-boundary error

NUL and other XML-unrepresentable characters formerly reached the document
library and produced a raw exception or generic service INTERNAL_ERROR. Export
now checks snapshot strings before creating the document-library object and
raises `ModelError` with `UNREPRESENTABLE_DOCX`, a location, code point and
offset. Both reject and allow policies reject these characters. Source streams
and heads remain unchanged; no character is silently deleted or replaced.

Tests cover all 29 excluded C0 controls and U+FFFE/U+FFFF, legal repertoire
boundaries, text/spans, title/font metadata, table cells, link targets and image
alternative text. Service-level NUL checks verify the stable error, nonretryable
and uncommitted response, durable retry receipt and preserved stream/head.
The native safe-ASCII model still supports its complete original 128 symbols.

## HF-03 — Corrected Unicode validation ordering

Malformed surrogate strings formerly raised UnicodeEncodeError while a direct
dictionary request was being serialized before typed validation. Request entry
now checks dictionary keys/values, nested list/tuple content and declared typed
request fields before strict UTF-8 serialization. Rejection is the stable
`VALIDATION_ERROR`, with no reserved request, job, document or other state change.
Tests compare every application SQL table and each in-memory semantic dictionary.

A targeted check also demonstrated the same ordering gap for an already typed
format request whose mapping value contained a surrogate. Shallow value
validation had not checked that mapping string. The entry check now covers it.
This is a verified direct library/typed-request boundary; actual SDK transport
exploitability is not inferred from it.

During this correction, an additional test caught an introduced guard defect:
`model_construct` can omit required fields, and direct attribute access raised
AttributeError before normal validation. The guard now skips missing values so
the ordinary validator can issue VALIDATION_ERROR. The failure and pre-correction
guard source are retained; a dedicated regression verifies state preservation.

## SH-D01 — Open intermittent service-harness cleanup error

One repeated existing test-suite run recorded a Windows `PermissionError`
(`WinError 32`) while removing the deadline test's `process-output.txt` after
the supervisor had reported its owned launcher stopped. This is a harness
cleanup failure, separate from the three format/ingestion product findings.
The failed run is retained in
`.docstream/format-hardening-runs/auth15-20261030/regressions-final.txt`.

The old service helper closes its Windows job and waits for the launch process,
but does not explicitly wait for all job descendants to reach zero. The
observation is consistent with the earlier native NH-D01 cleanup race; the
specific file-handle owner was not independently attributed. The native helper
already has a descendant wait, and was left unchanged.

An isolated retry after the full-service run also failed with WinError 32 on
the same temporary log boundary. The original failure and retry logs remain.

AUTH-15 covers the three named product corrections and their harness expectation
updates. It does not silently expand into repair of this older process-owner
helper. No change was made to `harness/runner.py`, its tests, or the native
cleanup implementation. The final validation report states the failed retry
outcome and current process inventory; passing product workloads do not erase
this verification error.

## Retained development evidence

The initial 11-method targeted run had 13 failed assertions and 37 errors;
these are test outcomes, not independent defect counts. Two early helper mistakes
in the new tests were corrected: looking up source identity in the ingestion
reply instead of the source record, and treating CellText as a flat text field
instead of joining its spans. The original logs remain. Subsequent tests added
exact harness-oracle checks, typed-mapping rejection and missing-field guard
coverage; the final targeted set has 15 methods.

All 24 previous failing inputs are copied byte-for-byte beside separately saved
cases with the approved expectations: five CR loss cases, ten specific DOCX
rejections and nine typed Unicode rejections. Their manifest retains original
file hashes, canonical case hashes, approved file hashes, rule labels and actual
results. Old case files were not edited to claim they had always passed.

No native representation, source-hash algorithm, database schema or package
dependency changed. No universal Word fidelity, security certification,
production-capacity guarantee or release acceptance follows from these tests.
Agentic-control integration remains the final stage and outside AUTH-15.
