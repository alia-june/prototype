# CPU contract — M1

Date: 2026-10-29. Implementation: docstream-cpu 0.2.0.dev1.

## Scope

The package is a CPU library with an ephemeral in-memory catalog. It has no
database, HTTP/MCP server, visual renderer, GUI, GPU backend, arbitrary-code hook,
or document-format parser. The preserved baseline remains separate. This is the
implemented CPU contract, extending the original Markdown-first representation
with immutable structured content and style data as approved for this slice.

## Values and identity

Snapshot schema: `docstream.snapshot/1`. Blocks have stable IDs, a kind, text,
typed style, and applicable heading/list metadata. Supported kinds are paragraph,
heading, code and list_item. Tables, images and inline spans are deferred.

Default styles are separate from explicit block overrides. A missing override is
represented by null and inherits the default. Font sizes and page dimensions are
positive integer millipoints; floats and numeric strings are rejected. Booleans
are exact booleans. Values and nested tuples/models are immutable.

Semantic hashes use sorted compact UTF-8 JSON without Unicode normalization.
Invalid unpaired surrogates are rejected. Raw source hashes apply to retained
original bytes. These are distinct representations; neither hash authenticates
the source or independently attests history.

Text ingestion accepts UTF-8/UTF-8 BOM bytes, preserves the original bytes and
newlines, explicitly removes only a leading encoding BOM from decoded text, and
creates one literal text block. It does not classify Markdown headings. Unsupported
encodings fail explicitly. Structured ingestion accepts a validated Snapshot.

Stream IDs describe occurrences. Different streams can refer to the same payload.
Every accepted transformation has a logical output stream, including changes
whose execution disappears. Each empty submitted batch also has a new result ID.
Operation IDs are unique within a batch; address them with their batch ID across
batches. The catalog prevents block-ID reuse along a stream lineage. Standalone
snapshot evaluation has no history unless reserved IDs are passed explicitly.

## Batch interface

Batch schema: `docstream.batch/1`, with `base_sha256` and an ordered `operations`
array. A batch has at most 256 operations. Each operation has a unique ID, an
explicit kind and integer version 1. Unknown fields/kinds, invalid targets,
incorrect scalar types, failed content guards and invalid positions fail.

`parse_batch` accepts a JSON string or dictionary through the same strict scalar
validation boundary. Input arrays become immutable tuples. The generated schema
is in CPU_BATCH_SCHEMA.json; some property-dependent value constraints are
enforced by semantic validators in addition to that structural schema.

| Kind | Fields beyond operation_id/kind | Exact meaning |
| --- | --- | --- |
| set_property | property, value | Assign title, default font, font size or page dimension. |
| set_style | targets, property, value | Assign font, size, bold or italic to explicit blocks; null removes an override. |
| restore_style | targets | Restore all explicit block style fields from the batch input, preserving inheritance. |
| set_font | font_family; scope=all_text | Set the default font and clear every current block font override, making the effective font uniform. |
| restore_font | none | Restore the batch-input default and original explicit font override for each current block. |
| replace_text | target, text, expected_text_sha256 | Replace a complete block's text only when its logical input digest matches. |
| insert_block | block, after | Insert a newly identified block after an existing block; null means the beginning. |
| remove_block | target | Remove a block from the new result; old streams retain it. |
| move_block | target, after | Move an existing block; null means the beginning. A block cannot follow itself. |

Restoring a block inserted after the batch baseline fails with RESTORE_BASE_MISSING;
the system does not guess its original style. Inserted IDs cannot be reused in the
same batch, even after removal. The catalog extends this restriction to lineage
history across batches. A later explicit restore operation can expand this policy
only under a separately agreed contract.

## Planning and execution

`plan(snapshot, batch)` validates every original operation in source order against
a mutable symbolic map. It does not create a complete snapshot or rendering after
every operation. The plan includes the full original batch, dependencies,
reductions, retained assignment cells/structural commands and an expected result
digest. It is deterministic for identical inputs and versions.

Assignment cells identify document properties or block-style properties. Between
text/structural barriers the reducer computes their final required writes:

- RED-01 absorbs duplicate absolute assignments.
- RED-02 removes writes superseded by a later absolute assignment.
- RED-03 removes cell writes whose exact final state equals the region input.
- RED-04 groups independent final cells in stable source order.

Reduction can affect part of a multi-target operation. Explanations identify the
affected cells and original operation IDs. No original catalog entry is deleted.
Unknown independence remains ordered. Text replacement and all structural commands
fence assignment regions; they are retained even if their net text effect cancels.

`reference_execute` performs all requests without reduction. `execute` consumes a
compiled plan, verifies its input/version/content seal and checks its resulting
semantic digest against the validated expected output. The seal detects accidental
change; it is not a signature or authorization boundary. Plans are trusted library
objects generated by the planner. A future service must accept server-owned plan
IDs, not treat caller-supplied plan hashes as execution permission.

Reference execution counts attempted assignment-cell writes, including assignments
equal to an existing value. Reduced execution counts only retained cell writes.
These are operation counters, not timings, VRAM estimates or speedup claims.

## Catalog lifecycle

`CpuModel.ingest` creates a root stream and head. `stage` validates a batch and
adds a Candidate plus its logical output streams. It does not move the head.
`materialize` constructs one requested stream/prefix and shares identical payloads.
`inspect` returns state/provenance; content inspection may materialize the result.
`history` follows input relationships. Inspection in any order leaves the head
unchanged.

`commit_semantic` checks the expected head/revision and explicitly advances the
in-memory head. Repeating it for the same candidate returns its recorded result.
It reports memory-only state; no durable idempotency receipt or visual rendering
is claimed. A competing candidate receives STALE_HEAD and remains inspectable.
Each method is protected by an instance lock; there is no cross-process owner or
durability yet.

To observe an intermediate state, stage/commit separate batches or inspect that
logical prefix. Reductions in a later batch cannot remove a recorded earlier
observation. Selective bypass and arbitrary operation execution order are absent.

## Reusable example and validation

From the service directory:

```powershell
.\.venv\Scripts\python.exe examples\font_example.py
.\.venv\Scripts\python.exe tests\run_validation.py
```

The example uses the maintained package and writes docs/font-example.json. It
retains four logical outputs for A -> B -> A -> C -> A, produces a distinct result
stream with identical semantic content, uses one stored payload and executes zero
reduced property writes. It explicitly reports not_rendered and memory_only.

No API currently implements visual preview, DOCX export, persistence, MCP discovery,
durable retries or GPU execution. Those remain the next implementation scopes.
