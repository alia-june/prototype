# Syn-Etabit Transformer — Textual

`syn-etabit-transformer-textual` is the canonical product name. **Syn means synthetic.** Etabit is the project spelling.

This repository directory is a curated export of the system formerly developed under the working names Docstream and Strmdocx. Those names remain in historical evidence and compatibility interfaces where they identify what was actually implemented or tested.

## Theoretical use cases

These are prospective uses of the architecture, not claims about presently shipped or production-ready capabilities.

### AI-native document genesis

An AI could originate a document directly as Markdown content plus a JSON-governed document plan. Text, structure, metadata, assets, transformations and emission requirements would retain separate referenced identities instead of being collapsed prematurely into one opaque office-document file.

### Non-destructive continuous revision

Every accepted edit could produce a new stream or revision rather than mutating the prior stream in place. A system could inspect transformations in chronological order, reverse order or selected logical order; compare any two retained states; and return to an earlier state by selecting it rather than reconstructing it through destructive rollback.

### Logical transformation reduction

A transformation catalogue could identify operations that cancel, supersede, repeat or make earlier operations observationally irrelevant before a document is rendered.

For example, changing a whole document's font, reverting it, changing it again and finally returning to the original font might require no final font mutation at all. The intermediate intent and provenance could remain inspectable even when the unnecessary physical operations are omitted from the resolved emission plan.

### Multi-format terminal emission

One resolved native Markdown/JSON state could be ejected as a complete immutable conversion package and passed through an admitted external adapter for DOCX, PDF, HTML or another target format. The emitted artifact and conversion receipt would remain derived outputs rather than becoming the native editable authority.

### Reference-addressed language assembly

Text could be represented through direct references across replaceable maps—for example symbols, glyphs or fragments, components, roots, words, sentences and paragraphs—without requiring every source or theory to share one permanent interpretation.

A later WordNet transmigration could retain source-derived records separately from decoded structures, native constructions, cross-relations and derived information. Each layer could identify its map, context, version and provenance.

### CPU-reference and later GPU execution

A deterministic CPU model could remain the semantic authority while a later GPU backend accelerates approved rendering, transformation resolution or reference traversal. GPU output would have to remain comparable with the CPU reference behavior rather than silently redefining it.

### Agent-operated document services

After the document model, transformation contracts, receipts, permissions and failure boundaries are stable, an agent could use the system as a document service instead of repeatedly generating temporary scripts to rebuild and convert documents. Agentic control remains a final integration layer, not a prerequisite for the native model.

## Direction

The forward model is Markdown-first, JSON-governed and reference-native:

- Markdown carries primary textual content.
- JSON carries document identity, structure, metadata, profiles, assets, transformation state and emission requirements by reference.
- Source content, transformations, resolved state and emitted artifacts retain distinct identities.
- Changes create new streams or revisions rather than destructively rewriting prior results.
- Ordered transformations may later be reduced when later operations make earlier operations observationally irrelevant, while the catalogue and provenance remain inspectable.
- CPU behavior is the reference model; GPU conversion is later work.
- Agentic control is the final integration stage.

Target documents cross an **Eject → Transform → Ejection** boundary: resolve and validate the native Markdown/JSON state, eject a complete immutable conversion package, transform it through an external target-format adapter, then retain the derived artifact and its receipt separately.

## Current implementation

The compatibility service is under [`service/`](service/README.md). Its existing identifiers remain unchanged:

- distribution: `docstream-cpu`
- module: `docstream_cpu`
- CLI: `docstream-local`
- protocol family: `docstream.*`
- local runtime state: `.docstream`

The service contains the CPU reference model, immutable semantic snapshots, typed transformations, logical output streams, an explainable reducer, SQLite-backed receipts and recovery, rendering, Markdown/DOCX adapters, and rigid/fuzzy/torture harnesses. Read the contracts and validation reports before treating any milestone result as general product acceptance. The retained product outcome records passing rigid and bounded torture checks with three fuzzy character/conversion finding groups.

## Repository boundary

This export omits installed Python environments, Playwright/Chromium distributions, mutable `.docstream` state, torture stores, caches, the WordNet payload and supplied third-party archives. See [`REPOSITORY_EXPORT.md`](REPOSITORY_EXPORT.md), [`INTEGRATIONS.md`](INTEGRATIONS.md) and [`docs/integrations/INTEGRATION_GATE.md`](docs/integrations/INTEGRATION_GATE.md).

No external integration is activated by cloning this repository.

