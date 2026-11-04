# Format and ingestion hardening contract

Date: 2026-10-30. Approved scope: AUTH-15.

The user explicitly approved correction of HF-01/HF-02/HF-03, including a
specific carriage-return conversion policy. The source basis is
PROJECT_DECISIONS.md, M4_FORMAT_CONTRACT.md, HARNESS_FINDINGS.md and
NATIVE_HARNESS_META_VALIDATION.md. Earlier reports remain historical evidence;
this contract records the newly approved behavior rather than rewriting them.

## Source fidelity and conversion

Native and semantic source strings remain exact. This increment does not change
source bytes, snapshot schemas, hashes, stream ancestry, native ASCII symbols,
head advancement or the database schema. DOCX exports create a representation
of an existing stream and never advance its head.

DOCX body text cannot retain the source distinction between carriage return and
line feed through this adapter's line-break mapping. The document library maps
each CR or LF to a line break, and reads line breaks back as LF. See the
[python-docx text API](https://python-docx.readthedocs.io/en/stable/api/text.html).
This explains the conversion behavior; the user's AUTH-15 approval establishes
the service policy.

For emitted paragraph/span/table-cell text and a displayed document title:

- Each CR maps to one LF in the exported representation. Existing LFs remain.
  Consequently CRLF maps to two line breaks; it is not collapsed to one.
- The adapter emits `DOCX_CARRIAGE_RETURN` with a bounded field location and
  description. It converts a temporary output string, never the stored source.
- The service's default `loss_policy=reject` returns `CONVERSION_LOSS`, retains
  the diagnostic in the failed request receipt and publishes no artifact.
- Explicit `loss_policy=allow` permits that conversion. The successful durable
  receipt retains its diagnostic. Repeating the same key returns the same
  receipt, including after restart.
- The core title metadata and displayed title use the same converted string,
  avoiding an artificial conflict when the resulting DOCX is reimported.

No general CR/LF equivalence is introduced. Metadata such as image alternative
text, font names and link targets is not passed through the paragraph conversion
helper. It is still checked for XML representability.

The low-level `export_docx` adapter retains its existing `(bytes, Losses)`
interface. Its caller must enforce the loss policy; the maintained FormatService
does so before publishing output. Direct adapter use alone is not an accepted
service export or implicit approval of losses.

## DOCX-unrepresentable characters

Before creating a document-library object, export preflight checks every string
in the materialized snapshot, including metadata, styles, runs, links, table
cells and image alternative text. Its repertoire follows the XML 1.0 `Char`
production: TAB, LF, CR, U+0020..U+D7FF, U+E000..U+FFFD and
U+10000..U+10FFFF. NUL, the other excluded C0 controls, surrogates and U+FFFE/
U+FFFF are outside that repertoire. This is based on the
[W3C XML 1.0 character specification](https://www.w3.org/TR/xml/#charsets).

An unsupported character raises the exact application error code
`UNREPRESENTABLE_DOCX`, with its field location, code point and character
offset. No source text is deleted, replaced or sanitized. Both reject and allow
policies return this error: accepting a reported conversion loss does not make
an unrepresentable character legal. Through the service, failure is nonretryable
and committed false; the failed request has a durable receipt. The original
stream and document head remain unchanged and no export artifact is published.

This DOCX-specific boundary does not prohibit those characters in the native
safe-ASCII model or otherwise redefine the semantic model's character domain.
It does not claim that every XML-legal character has a visible glyph or that
Word layout is certified.

## Unicode request entry

Before strict UTF-8 serialization, request parsing checks strings throughout
dictionary/list/tuple containers, dictionary keys and declared fields of typed
request values. Invalid surrogate strings produce `ModelError` with
`VALIDATION_ERROR`. The check applies to both direct dictionaries and typed
request instances, including mapping fields that their shallow value validator
does not inspect.

Malformed Unicode is rejected before request reservation, jobs, receipts,
documents, sources, payloads, heads or artifacts are mutated. The tests compare
all application SQL tables and all in-memory semantic dictionaries. No failed
receipt is required for an input rejected before reservation. Valid UTF-8,
combining sequences, supplementary scalars and original CR/LF bytes retain their
current values and hashes.

The existing typed validation and strict JSON normalization still run after
this check. This increment is not a general arbitrary-Python-object protocol,
cycle support, expanded request budget or transport exploitability claim.

## Harness expectations and proof

Service harness reporting is `docstream.harness/1.1`; closed case schema `/1`
and the existing 117-regression selection remain compatible.

Seeded generation declares expected behavior from fixture text independently
of product execution: NUL DOCX cases require `UNREPRESENTABLE_DOCX`; CR DOCX
cases explicitly allow `DOCX_CARRIAGE_RETURN`; other cases retain their original
expectations. Unexpected errors and successful acceptance of an expected
rejection fail. Merely reporting some loss cannot excuse another text change.

For the specifically approved CR loss, the comparator changes only the expected
title/body/span/cell CR characters to LF, then compares the complete remaining
supported meaning. Styles, ordering, structure, other text and image metadata
remain significant. Missing loss diagnostics or an unrelated content change
fail dedicated tests. Original historical cases and expectations stay intact;
new approved cases are stored separately with source hashes and rule labels.

## Outputs, limits and exclusions

The implementation changes request validation in `service.py`, DOCX export in
`docx_adapter.py`, and the service harness's generator/execution expectations
and reporting identity. Targeted verification is maintained in
`tests/test_format_hardening.py`. Actual evidence is under
`.docstream/format-hardening-runs/auth15-20261030/`, with fresh native/service
runs in their established run areas. Companion reports are
FORMAT_HARDENING_VALIDATION.md and FORMAT_HARDENING_FINDINGS.md.

Full service validation retains 500 fuzzy cases, four clients/1,800 loop
requests, at most 2,000 torture service calls, 20 crash cycles, 25 render calls,
1,200 seconds and 512 MiB of retained evidence. Native validation retains
100/1,000/eight, 2,000 submitted attempts, 900 seconds and 512 MiB. Additional
verification covers the affected boundaries and relevant existing harness tests.
No dependency installation or database migration is required. Package metadata
remains 0.2.0.dev4 for this local corrective increment; source manifests identify
the exact changed implementation. No release packaging, GPU, bypass, vocabulary
ingestion, host configuration or agentic-control integration is included.
