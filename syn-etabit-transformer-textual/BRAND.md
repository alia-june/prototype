# syn-etabit-transformer-textual

Display name: **Syn-Etabit Transformer — Textual**  
Effective date: 2026-11-03  
Status: canonical prospective product brand.

## Identity

`syn-etabit-transformer-textual` is the canonical product name for the forward development of the system formerly developed under the working names **Docstream** and **Strmdocx**.

The spelling is **Etabit**. Earlier occurrences of Edabit in historical material are retained where they are evidence of the original wording; they are not the current product spelling.

The token `syn` means **synthetic** by later direct user decision. It does not mean synchronization or another expansion unless a later decision changes it.

## Product direction

Syn-Etabit Transformer — Textual is Markdown-first, JSON-governed and reference-native.

- Markdown carries primary textual content.
- JSON carries document identity, structure, metadata, profiles, assets, transformation state and emission requirements by reference.
- Source content, transformations, resolved state and emitted artifacts retain distinct identities.
- Word documents are derived emissions rather than the intermittently edited native document.
- A requested correction creates a new internal revision and a new emission; it does not require destructive editing of the prior emitted artifact.
- Agentic control remains the final integration stage.

## Eject → Transform → Ejection

The forward output boundary is:

```text
Markdown content
      +
JSON document plan
      +
referenced structures, profiles and assets
      +
cataloged transformations
             ↓
resolved and validated document state
             ↓
Eject a complete immutable conversion package
             ↓
Transform through an external target-format adapter
             ↓
Ejection of the derived artifact and conversion receipt
```

The external conversion boundary is a design direction, not a claim that the existing compatibility service has already removed or replaced its implemented Markdown/DOCX adapters. The current runtime and its historical validations retain their stated capabilities and limits until a separately approved migration changes them.

## Compatibility names retained in Phase 1

| Surface | Retained identifier | Phase 1 treatment |
| --- | --- | --- |
| Python distribution | `docstream-cpu` | Unchanged compatibility name |
| Python module | `docstream_cpu` | Unchanged compatibility namespace |
| CLI entry point | `docstream-local` | Unchanged compatibility command |
| Protocol/schema family | `docstream.*` | Unchanged compatibility identifiers |
| Local state directory | `.docstream` | Unchanged compatibility location |
| Workspace directory | `strmdocx` | Unchanged physical path |
| Completed evidence | Docstream/Strmdocx wording | Preserved as historical evidence |

These identifiers do not replace the new canonical brand. They remain operational compatibility surfaces until an independently scoped machine-namespace migration is designed, approved and validated.

## Historical preservation

The rebrand is prospective. It must not silently rewrite:

- source archives;
- completed validation reports;
- manifests or their covered bytes;
- dated status statements;
- historical authorization records;
- test fixtures and expected protocol values;
- stored receipts or database records; or
- claims about which named implementation was actually tested.

When a historical record says Docstream or Strmdocx, that name remains part of the evidence. Forward-facing documents may identify those names as former working names without pretending the past artifact used the later brand.

## Not authorized by this brand decision

The Phase 1 rebrand does not authorize:

- renaming the workspace;
- renaming the distribution, Python package or CLI;
- changing protocol IDs, schema IDs or tool names;
- migrating `.docstream` state;
- changing a database schema;
- changing runtime behavior;
- removing current format adapters;
- implementing the external converter;
- changing completed pilot or inspector packages;
- publication, release or repository migration;
- GPU work; or
- agentic activation.

Each material migration remains behind its own production proposal and approval.
