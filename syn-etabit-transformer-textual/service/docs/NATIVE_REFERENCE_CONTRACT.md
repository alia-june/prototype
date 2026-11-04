# Native reference contract — safe ASCII CPU increment

Date: 2026-10-29 (America/New_York). Approved scope: AUTH-12.
Native profile: `docstream.native.safe-ascii/1`.

## Purpose and authority

The user approved a self-contained CPU test model after defining separate
symbol, glyph, component, root, word and larger-assembly layers. Entries have
identity and exact construction, without embedded linguistic meaning. A hyphen
is an actual symbol. The initial test base is the 128 ASCII positions; this
supersedes the earlier CP437 choice for this increment only.

This package is an in-memory reference implementation under
`docstream_cpu.native`. It does not replace the existing snapshots, batch
schema, persistence or service tools. No native service endpoint, visual
renderer, font system, dictionary, morphology inference or GPU backend is added.
The ordinary package version remains 0.2.0.dev4; the native contract/profile has
its own explicit version. Existing harness findings remain open.

The implementation adapts principles, not source classes, from the reviewed
catalogues: PP7-001/SHH-014 for identity scopes, SHH-003/SHH-051 for complete
publication, SHH-007 for no-op occurrences, and SHH-026/SHH-054 for explicit
resource accounts. No supplied pipeline code is executed or integrated.

## Symbols and exact bytes

`Alphabet` contains exactly 128 frozen `SymbolRef` values, numbered 0..127.
There is no dependency on a downloaded codepage. Each symbol expands to its
identical byte. NUL, tab, CR, LF, DEL, spaces, punctuation and letter case retain
their distinct values. No control is executed or interpreted by the model.

`ascii_symbols(str_or_bytes)` is literal conversion, not lexical parsing. It
returns an immutable tuple of symbol references. Non-ASCII bytes, Unicode
characters outside ASCII, malformed surrogates, coercible scalar values and
mutable byte arrays are rejected. No replacement, trimming, case folding,
transliteration or newline normalization occurs. Maximum literal length is
10,000 symbols. Empty literals are valid.

Symbol values are a seven-bit logical domain. References are Python values in
this CPU implementation; no compact GPU address width or physical one-byte
assembly storage claim is made. The assembly catalogue can exceed 128 entries.

## Structural definitions

`Layer` explicitly orders: GLYPH, COMPONENT, ROOT, WORD, PHRASE, SENTENCE,
PARAGRAPH, DOCUMENT. Symbol references are below every assembly layer.

`define(layer, children)` accepts an explicit Layer member and an exact tuple
of SymbolRef/AssemblyRef values. Each assembly reference must already exist in
the same catalog and must belong to a strictly lower layer. Direct references
can skip unused layers; this permits literal fallback without inventing roots.
Same-layer and upward references are rejected. Construction order and decreasing
layers prevent cycles; there is no arbitrary graph-import parser in this scope.
Glyph width is not fixed at two symbols. Empty assemblies are valid.

An assembly payload contains only:

```json
{
  "schema_version": "docstream.native.assembly/1",
  "profile": "docstream.native.safe-ascii/1",
  "layer": "glyph",
  "children": [
    {"kind": "symbol", "value": 101},
    {"kind": "symbol", "value": 116}
  ]
}
```

An assembly child instead uses
`{"kind":"assembly","definition_id":"<64 lower-case hex digits>"}`.
The definition ID is SHA-256 of sorted compact ASCII JSON with these fields.
It binds the profile, structural layer and ordered references. Labels, word
meanings, etymology, prefix/suffix behavior and font are not payload fields.
The structural Layer is an explicit construction constraint, not a linguistic
classification inferred from spelling. Fixture labels live outside payloads.

Identical definitions reuse an ID and stored payload. Equal expanded bytes can
have different definition IDs when their layer or composition differs. A root
and a completed word may therefore share bytes without sharing identity.

Frozen dataclasses, immutable child tuples and read-only catalog snapshots
protect the public value API. This is not isolation from hostile Python code
with access to private attributes or object mutation primitives.

## Worked construction

```python
from docstream_cpu.native import Layer, NativeModel, SymbolRef, ascii_symbols

model = NativeModel()
et = model.define(Layer.GLYPH, ascii_symbols("et"))
te = model.define(Layer.GLYPH, ascii_symbols("te"))
ette = model.define(Layer.COMPONENT, (et, te))
hyphen_ette = model.define(Layer.COMPONENT, (SymbolRef(45), et, te))
base = model.define(Layer.ROOT, ascii_symbols("marion"))
word = model.define(Layer.WORD, (base, ette))

assert model.expand(ette) == b"ette"
assert model.expand(hyphen_ette) == b"-ette"
assert model.expand(word) == b"marionette"
```

The fixture's `marion` label demonstrates spelling construction, not an
etymological assertion. `ette` and `-ette` use the same glyph definitions; their
component definitions remain different because the latter contains a hyphen.
Both glyph and component forms of `un` and `er` are fixture-tested separately.

## Streams, occurrences and inspection

`create_stream(root)` retains an assembly root as a new stream occurrence. IDs
are model-namespace UUID plus a local monotonic ordinal; they are not payload
digests, credentials or durable cross-process identifiers. Definitions can have
matching IDs across models, but references still must be registered locally.

`stream(id)` returns an immutable Stream record. `inspect(id, path=())` selects
an occurrence by an exact tuple of zero-based child positions from that stream's
root. It returns the selected reference, structural layer (or None for a
symbol) and expansion byte length. Paths are structural positions, not byte,
Unicode, word or visual offsets. Each intermediate transformation has its own
root and hence its own path context. Maximum path length is eight.

`expand(reference)` and `expand_stream(id)` return exact bytes. `escaped(id)`
returns quoted ASCII inspection text with controls escaped. It is a diagnostic
view, not a visual document rendering or a replacement for the byte payload.
`history(id)` returns immutable ancestry from origin to the selected stream.
Reading history or inspecting an older prefix does not select a new head.

There is no implicit mutable document head or external commit in this package.
Applying two batches to one retained base creates two branches. Publication in
this catalog means only an in-memory update; it is not an existing service
document commit, database transaction, renderer publication or durable receipt.

## Structural edits and atomic batch publication

`apply_batch(base_stream_id, operations)` takes an exact tuple of immutable
Edit values. Each operation has a unique ASCII operation_id within that batch.
The batch also has its own identity, so a local operation ID may be reused in
another batch without confusing the two occurrences.

| Kind | Required fields | Effect |
| --- | --- | --- |
| insert | path, index, count=0, nonempty references | Insert references before the selected assembly child index. Index equal to child count appends. |
| remove | path, index, positive count, empty references | Remove the selected consecutive child references. |
| replace | path, index, positive count, nonempty references | Replace the selected consecutive references. |

The path selects an assembly, not a symbol. Index/count are exact nonnegative
integers within its current child range. A batch processes operations in request
order, and each path resolves against its logical input from the preceding
operation. Inserted children must obey that parent's structural-layer rules.

Only the selected occurrence's ancestry is rebuilt. Other occurrences of a
shared word, root or glyph retain their old references. New definitions are
content-addressed and old definitions remain available. No definition is edited
in place. This is explicit structural editing, not automatic lexical analysis.

Every accepted operation produces a distinct stream with parent, batch and
operation IDs. The batch retains the exact Edit tuple and a request digest over
the profile, base-stream ID and operation records. `batch(id)` returns that
immutable record and all logical output IDs. An empty batch produces one new
stream referring to its input root. A content-preserving edit still has a stream
occurrence and can reuse the old definition ID.

Definitions, derived size/work accounts, every prefix stream, the batch record
and ID counters are prepared locally. Only after all operations and output
preparation succeed is one catalog-state pointer replaced under the instance
lock. A late validation/resource failure publishes no prefix, definition,
counter change or history record. The tests also inject a failure while preparing
the read-only output maps to verify this publication boundary.

This package does not claim service idempotency or automatic edit elimination.
Submitting identical work again creates another occurrence. Definition reuse
avoids duplicate storage of the same construction; operations are still
validated/evaluated. The existing font reducer remains a separate implementation.

## Resource bounds and errors

| Default limit | Value |
| --- | ---: |
| Base symbols | 128 |
| Definitions | 4,096 |
| Stored direct reference slots across all definitions | 5,100,000 |
| Children per definition | 10,000 |
| Expanded bytes per definition | 1,000,000 |
| Traversal steps per definition | 2,000,000 |
| Streams | 4,096 |
| Batches | 2,048 |
| Operations per batch | 256 |
| Occurrence-path depth | 8 |

`Limits` can lower or explicitly configure most resource accounts within the
validated CPU ceilings. Children/path/operation ceilings are fixed by this
profile. Strict lower-layer edges bound depth. The definition's byte length and
traversal work are calculated before it can be registered: one visit for the
assembly plus each referenced symbol/subassembly expansion. An empty shared
subgraph can therefore exhaust the traversal budget even with zero output bytes.
Equal reused definitions do not consume new reference slots. Old definitions
remain retained, so edits can eventually reach a catalog limit by design.

These are operation/count bounds, not a hard wall-clock deadline, measured
maximum memory guarantee, leak-absence proof or production capacity promise.

NativeError carries a stable code: VALIDATION_ERROR, UNKNOWN_REFERENCE,
LAYER_MISMATCH, LIMIT_EXCEEDED, UNKNOWN_STREAM, UNKNOWN_BATCH, INVALID_PATH,
INVALID_RANGE, DUPLICATE_OPERATION or INVARIANT_ERROR. Some malformed path scalar
values use VALIDATION_ERROR; structurally invalid paths use INVALID_PATH.
Python dataclass unknown-field errors remain ordinary TypeError; no external
JSON request parser or transport error mapping is provided by this increment.

## Validation entry point and later work

From the service directory in the prepared project environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_native.py -v
```

Fixed expectations, 200 seeded cases with a separate byte-sequence oracle, and
10,000-reference/500-transformation work are retained in the maintained tests.
Actual results and proof limits are in NATIVE_REFERENCE_VALIDATION.md.

Deferred: vocabulary/WordNet ingestion, inferred fragmentation, linguistic
classification, automatic reduction of native edits, per-system maps beyond
this profile, compact binary/GPU representation, persistence, existing-service
integration, visual rendering, release packaging and agentic-control activation.
The latter remains the final integration stage. Existing HF-01/HF-02/HF-03
findings are neither corrected nor cleared by this native test slice.
