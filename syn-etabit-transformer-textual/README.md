# Syn-Etabit Transformer — Textual

`syn-etabit-transformer-textual` is the canonical product name. **Syn means synthetic.** Etabit is the project spelling.

This repository directory is a curated export of the system formerly developed under the working names Docstream and Strmdocx. Those names remain in historical evidence and compatibility interfaces where they identify what was actually implemented or tested.

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

