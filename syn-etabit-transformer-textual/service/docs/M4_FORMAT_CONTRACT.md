# M4a document format contract

Date: 2026-10-29. Implementation: docstream-cpu 0.2.0.dev4.

The user approved this scope by replying "yes approved" to the concrete M4a
proposal. It covers richer semantic content, Markdown/DOCX import and export,
managed images, explicit losses, service operations and bounded validation.
Agentic-control integration remains the final stage. Release/installer work,
GPU execution, selective bypass and Word-layout certification are outside M4a.

## Representation and compatibility

`docstream.snapshot/1` and its original Block schema are unchanged. Existing
snapshots are read without promotion or hash rewriting. Stored version-one
plans still use reducer version 1 and are recompiled/checked at startup. Version
two uses `docstream.snapshot/2`, Snapshot2 and RichBlock. Both versions are
accepted by structured ingestion and are supported by the catalog, persistence,
planner, semantic executor, preview and export paths.

Version two adds:

- Inline spans with text, nullable font/size/bold/italic overrides, inline-code
  status and an optional HTTP/HTTPS/mailto hyperlink without credentials.
- List depth 0 through 8 and an explicit list start value. Every list item is
  one text paragraph. A list cannot begin below depth zero or skip parent levels.
- Rectangular tables with up to 32 columns and 1,000 rows. Each cell contains
  one or more text paragraphs with spans. Each row has an explicit header flag.
- Image references with SHA-256, PNG/JPEG media type, alternative text, and
  positive integer millipoint width and height.

Text blocks retain a `text` field that must exactly equal concatenated span
text when spans are present. Table/image blocks cannot also carry text/spans.
All values remain immutable and strict. Original source bytes and semantic JSON
are distinct records. Hashes establish byte identity rather than source authority.

No database migration is required: snapshots already contain versioned JSON;
managed images reuse the existing transactional sources table with IDs
`asset:<sha256>` and media type as their encoding marker. Database schema stays
2. No existing database was rewritten for M4a. A copy of the actual M3 example
store is used for compatibility validation.

## Transformations and inspection

Existing operation kinds remain available. `set_font(all_text)` clears current
explicit font overrides in blocks, inline spans and table-cell spans while
setting the document default. `restore_font` restores their exact batch-input
values. These nested assignments use the same conservative reduction rules.
`set_style`/`restore_style` address explicit block styles; nested explicit span
overrides continue to take precedence. They do not claim to restyle every span.

`replace_text` rejects blocks containing spans, tables or images. The new
`replace_block` operation requires a version-two block, the same block ID and
`expected_block_sha256` computed from the complete current block JSON. It is an
ordered structural barrier. It permits deliberate changes to spans, tables and
image references without silent flattening. Inserted blocks must match their
snapshot version. Use a fully serialized RichBlock for a version-two insertion;
a minimal version-one block is not implicitly upgraded.

Structural operations must leave every logical list output valid, including
intermediate prefixes. Remove nested children before removing their parent, or
explicitly change their depth before moving them. A single-block move does not
implicitly move a whole subtree. Missing baseline styles make restore fail
instead of inventing an original value.

`docstream_inspect` adds `section: structure`, optional `block_id`, and a `path`
array of field names/array indices. Strings and arrays are paginated with the
existing offset/limit. Dictionaries paginate their fields. An oversized reply
requires a narrower path/page. For example, a table-cell span can be inspected
with `["rows",1,"cells",0,"paragraphs",0,"runs",0,"text"]`.

## Format fidelity matrix

| Feature | Markdown import/export | DOCX import/export |
| --- | --- | --- |
| Paragraph text and line breaks | CommonMark text, hard breaks and soft-break spaces | Body paragraph/run text and text-wrapping line breaks |
| Headings | Levels 1–6, explicit source syntax | Built-in Heading1–Heading6 or an explicit based-on chain |
| Title | Separate bundle property; ordinary headings remain headings | Core title metadata and an initial Title paragraph map to the title property; conflicts report a loss |
| Bold and italic | Inline emphasis; exporter reparses and compares supported meaning | Supported direct/inherited font properties; original style definitions are not reproduced |
| Fonts and sizes | Properties retained in bundle metadata; explicit block/run font styling reports a loss | Explicit font properties and resolved Latin theme/default fonts; half-point size rounding reports a loss |
| Inline/block code | Inline backticks and fenced/indented blocks; language metadata reports a loss | Explicit DocstreamInlineCode/DocstreamCode styles in generated output |
| Hyperlinks | HTTP/HTTPS/mailto; unsupported targets/titles report losses | Explicit external hyperlink relationships; internal/bookmark targets report losses |
| Lists | Ordered/bullet lists, start and nesting; multi-paragraph/code/table list containers report losses | Explicit numbering definitions with bullet/decimal levels; other numbering formats report losses |
| Tables | Enabled markdown-it table extension; first header comes from syntax | Rectangular body tables and explicit repeat-header flags |
| Headerless tables | Export reports a loss and inserts an empty header only with accepted losses; data is not promoted | Preserves header flags without inventing a header |
| Multiple cell paragraphs | Export reports a loss before joining them with spaces | Preserved as ordered cell text paragraphs |
| Images | Standalone images from supplied local assets; dimensions retained in bundle metadata | Standalone embedded inline PNG/JPEG, alternative text and dimensions |
| Source bytes | Exact original Markdown or bundle retained | Exact original DOCX ZIP retained |
| Page layout | Not a Markdown guarantee | Page size retained; controlled output margins/presentation; no Word pagination equivalence |

Markdown uses markdown-it-py 4.2.0, CommonMark preset plus the table rule. This
is a declared subset, not a claim of full CommonMark or GitHub Markdown
conformance. Raw HTML is parsed as an unsupported token and never executed.
Block quotes, rules, missing/external images, inline image mixtures, alignment
and other unsupported constructs produce diagnostics. Code final-newline,
empty-paragraph and delimiter ambiguities are also reported when exporting.

Markdown exports are ZIP bundles containing `document.md`, `docstream.json`
with schema `docstream.markdown-bundle/1`, document properties and image sizing,
and hash-named assets. Opening document.md in another application does not apply
Docstream's property/image metadata. Reimport the complete bundle to retain it.
Source block IDs and source style definitions are not a portable identity promise.

DOCX is processed with python-docx 1.2.0 and bounded OOXML inspection. Known
semantic styles map to the service's presentation. Original paragraph spacing,
table appearance, theme definitions, style definitions and exact layout are not
round-trip promises. Detected unsupported direct placement/font effects, used
style color/effects, unknown paragraph styles, section margins/sections, headers,
footers, comments, tracked changes, fields, content controls, alternate content,
foreign vocabularies, floating objects, merged/nested tables and external
non-hyperlink relationships produce diagnostics. Detection is conservative;
this is not an exhaustive validator for every possible OOXML feature.

## Loss policy and source boundary

ImportRequest: `request_key`, `format` (`markdown`, `markdown_bundle`, `docx`),
`data_base64`, optional name-to-base64 `assets` for Markdown, and `loss_policy`
(`reject` by default, or `allow`). ExportRequest: request_key, stream_id, format
(`markdown_bundle`, `docx`) and the same loss policy.

Detected losses under `reject` return CONVERSION_LOSS with bounded structured
diagnostics, and do not create a document/export. `allow` is an explicit request
to accept the reported mapping; diagnostics remain in its durable receipt.
It does not enable unsupported execution, arbitrary file access, external
fetching or automatic support for malformed structures. Some inputs remain
unrepresentable and fail even under allow. Rejected originals remain in the
reserved request payload; accepted originals also have source records.

Import creates a new document/head at revision zero. Exports materialize a
stream and publish an artifact; they never advance a document head. Request
keys retain the existing durable retry/conflict behavior. A missing export
artifact makes replay return ARTIFACT_UNAVAILABLE while retaining its receipt;
a new export key repairs it. Original sources, old streams and failure evidence
are not overwritten to implement a new conversion.

No caller file path, script, external executable or importable module is accepted
by these operations. Base64 bytes and explicit asset identifiers are data.

## Bounds, publication and rendering

Combined source/supplied image bytes: at most 1 MiB, with a conservative base64
input bound before receipt reservation. Up to 64 separately supplied assets.
ZIP packages: at most 256 entries, 16 MiB total expanded bytes, and a further
large-entry expansion-ratio bound. Unsafe paths, name normalization, duplicate
or case-aliased entries, linked/encrypted entries, DTD/entity declarations and
invalid XML are rejected. Nothing is extracted to caller-named filesystem paths.

Images: at most 1 MiB each, static PNG/JPEG only, at most 16 million pixels,
verified with Pillow. Referenced bytes and media types are rechecked for preview
and export. An unavailable asset prevents a rendered/semantic committed result.
The network body remains 2 MiB, semantic inputs/results 1 MiB, structured replies
128 KiB, batches 256 operations and ordinary inspection pages at most 100 items.
Export artifacts are capped at 32 MiB. An export can exceed the current import
cap, so successful export alone is not proof that a large result can be reimported.

DOCX/ZIP artifacts use hash-named managed files, temporary write/fsync/rename,
and ready metadata inside the same transaction as the export receipt. A file
left by a failed publication is unadvertised. A detected damaged destination
is quarantined before repair. Downloads/chunks use the existing authentication.

HTML renderer version `docstream.html/2` adds spans, nested lists, tables and
embedded data images. All text is escaped; source markup is not executed.
Network requests and service workers remain blocked. The content/profile/font/
backend cache key includes the richer snapshot digest. Supported text fonts
remain the registered Arial, Times New Roman and Consolas families. Import may
retain another resolved font; preview then fails explicitly until it is changed
to an available font. No silent font alias was added.

Version-two code spans/blocks follow the same nullable-font inheritance as other
text. Code status supplies structure/presentation but does not silently override
an all-text font change. Assign Consolas explicitly when monospace is intended.
The legacy version-one code-font render-profile behavior remains available for
old streams; that profile field does not override version-two semantic fonts.

## Primary references

- https://spec.commonmark.org/0.31.2/
- https://markdown-it-py.readthedocs.io/en/latest/using.html
- https://python-docx.readthedocs.io/en/latest/user/text.html
- https://python-docx.readthedocs.io/en/latest/api/document.html
- https://python-docx.readthedocs.io/en/latest/dev/analysis/features/shapes/picture.html

Actual results and remaining limits are in M4_VALIDATION.md. Generated request,
snapshot and operation schemas describe structure; semantic validators add the
conditional and preservation rules described here.
