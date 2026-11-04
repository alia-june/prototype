# Syn-Etabit Transformer — Textual

`syn-etabit-transformer-textual` is the canonical product name. **Syn means synthetic.** Etabit is the project spelling.

This repository directory is a curated export of the system formerly developed under the working names Docstream and Strmdocx. Those names remain in historical evidence and compatibility interfaces where they identify what was actually implemented or tested.

## Etabit Drive construction

The **Etabit Drive** is the intended reference-addressed substrate beneath Syn-Etabit Transformer — Textual. It is not conceived as one flat document, one mutable database table or one permanently privileged interpretation. It is a composition of separately identified maps whose entries, order, structure, context and derivation remain directly addressable.

The current repository proves portions of this model through an immutable CPU catalogue and a bounded relative-map probe. It does **not** yet prove a mounted Etabit path, durable on-disk encoding, live map API, multi-writer locking, crash recovery or production persistence. The construction below is the intended logical architecture and the boundary that a later physical Etabit implementation must satisfy.

### Construction overview

```text
base symbol maps
        │
        ▼
glyph and fragment maps
        │
        ▼
component maps
        │
        ▼
root and word maps
        │
        ▼
phrase, sentence, paragraph and document maps
        │
        ├──────────────┐
        ▼              ▼
occurrence streams     transformation catalogues
        │              │
        └──────┬───────┘
               ▼
        resolved document state
               │
               ▼
     Eject → Transform → Ejection
```

Parallel map families provide the interpretation needed to construct and resolve those text structures:

```text
source maps
    ├── source-record order maps
    ├── decoded-structure maps
    ├── external-relation maps
    └── source evidence and locators

generic maps
    ├── objects
    ├── orders
    ├── structures
    └── processes

interpretive maps
    ├── grammar drives
    ├── syntax drives
    ├── theory drives
    └── derived relation drives

governing maps
    ├── contexts
    ├── selections
    ├── replacement ledgers
    └── derivation ledgers
```

No one map silently absorbs all of these roles.

### 1. Base symbol maps

The current safe construction begins with exactly 128 logical symbol positions corresponding to ASCII values `0..127`.

Each position is a direct one-to-one symbol reference:

```text
0   → NUL
9   → tab
10  → LF
13  → CR
32  → space
45  → -
65  → A
97  → a
127 → DEL
```

A symbol is retained as a value, not executed as a control and not interpreted as linguistic meaning. CR and LF remain different symbols. Uppercase and lowercase remain different. Punctuation, spaces and controls are not normalized away.

This is a logical symbol map, not a claim about a final physical bit width, disk sector, GPU address or packed binary representation.

A later repertoire can exist as another explicitly identified symbol or code-page map. An HTML map, Python map, CP437 map or another system-specific map does not redefine the safe-ASCII map in place. It becomes another addressable map associated with an explicit profile and context.

### 2. Structural assembly maps

Symbols are assembled through explicit structural layers:

```text
symbol
  ↓
glyph
  ↓
component
  ↓
root
  ↓
word
  ↓
phrase
  ↓
sentence
  ↓
paragraph
  ↓
document
```

A construction contains an exact ordered sequence of references to symbols or previously defined lower-layer assemblies. A direct reference may skip unused layers; the system does not have to invent a root or component merely to fill every possible category.

The structural layer constrains construction. It does not assert linguistic meaning.

For example:

```text
symbols 101, 116       → glyph "et"
symbols 116, 101       → glyph "te"
glyph "et" + "te"      → component "ette"
symbol 45 + et + te    → component "-ette"
structural root bytes  → root "marion"
root + component       → word "marionette"
```

In the current fixture, `marion` is a structural label, not an etymological claim. `ette` and `-ette` are different definitions because the second construction includes the literal hyphen symbol. Neither construction automatically means “suffix,” “subtraction,” “feminine,” or anything else.

Identical expanded bytes may have different identities when their structural layer or composition differs. Conversely, an identical definition recipe can reuse its existing identity.

### 3. Content-addressed definition identity

A native assembly identity binds at least:

- the schema and construction profile;
- the structural layer;
- the exact ordered child references.

The existing CPU reference model calculates the definition ID from canonical JSON using SHA-256.

Therefore:

- changing a child changes identity;
- changing child order changes identity;
- changing the layer changes identity;
- changing the profile changes identity;
- rebuilding an identical definition reuses identity;
- labels and meanings remain outside the meaning-free construction payload.

The definition is immutable. A later edit creates or selects another definition; it does not rewrite the previous definition's children.

### 4. Map identity

A higher Etabit map binds:

- map kind;
- map name;
- positive version;
- context identifier;
- exact ordered input-map identities;
- exact ordered canonical entries;
- schema and profile identity.

Its identity changes when any identity-bearing part of that recipe changes.

Order is therefore not incidental storage layout. It is a first-class referenced map. The same objects under a different order map form a different construction.

A durable reference must qualify the thing being referenced with its map identity, version and context. A bare word, object or category identifier is insufficient because the same entry can participate in multiple maps and interpretations.

### 5. Generic construction drives

The base generic drives are:

- **objects** — the addressable things involved;
- **orders** — how referenced things are sequenced;
- **structures** — how referenced things are related or assembled;
- **processes** — how inputs are selected, resolved or transformed.

Grammar and syntax are separate referenced drives. A theory drive consumes or relates those maps but does not become a permanently privileged foundation.

Government and Binding Theory, for example, can be represented as one theory projection. It is not hard-wired as the only interpretation. Another theory projection can be constructed and selected by a different context.

The current relative-map probe demonstrates this replacement mechanically with placeholders. It does not claim that either placeholder contains an authoritative linguistic theory.

### 6. Source transmigration

A source such as WordNet is not copied wholesale into one final Etabit map.

A controlled transmigration separates at least:

```text
raw source evidence map
        ↓
decoded source-structure map
        ↓
native construction map
        ↓
external-relation maps
        ↓
theory-relative relation maps
        ↓
composed lexical drives
        ↓
inference, synthesis and enrichment maps
```

The source map retains archive-derived facts, exact locators and source relationships. Decoding remains distinguishable from source bytes. Native word construction remains distinguishable from decoded source records. Inference and later enrichment remain distinguishable from both.

The resulting Etabit system may contain more information than the source archive, but additional information must identify its derivation and must not be presented as if it came directly from the archive.

### 7. Contexts and selections

Etabit has no single mutable global interpretation head.

A context map selects exact input maps for named roles. Resolving a role requires an explicit context reference.

For example:

```text
Context A v1 → composition A
Context B v1 → composition A
Context A v2 → composition B
```

Creating Context A v2 does not alter Context A v1, Context B v1 or composition A. Each remains addressable.

This is the operational meaning of “everything is relative and replaceable.”

Replacement creates a traceable alternative or successor. It does not erase the displaced map, rewrite its evidence or require a later rollback to reconstruct it.

### 8. Replacement and derivation ledgers

A replacement should retain references to:

- the prior map or composed drive;
- the replacement map or composed drive;
- the prior context;
- the new context;
- the reason or governing decision;
- the derivation recipe;
- the evidence identities involved.

A derivation ledger separately records how an output map was constructed from its ordered input maps.

The ledgers allow a reader or service to answer:

- What was selected?
- Under which context?
- What did it replace?
- What remains valid elsewhere?
- Which source and interpretation maps contributed?
- Which process and order were used?
- Can the construction be replayed?

### 9. Streams and transformations

A stream is an occurrence of a selected assembly root. Multiple streams can refer to the same immutable definition without becoming the same occurrence.

An accepted edit produces a new retained stream. Only the selected occurrence ancestry is rebuilt; shared definitions elsewhere remain unchanged.

The transformation catalogue retains:

- the base stream;
- ordered operations;
- each intermediate stream;
- parentage;
- batch and operation identities;
- the request digest;
- the logical outputs.

A later reducer may determine that some transformations cancel, repeat, supersede or are observationally irrelevant. Omitting unnecessary physical work does not require deleting the retained transformation history.

### 10. Atomic publication

A batch is prepared before it is published.

The current reference model follows this sequence:

1. Validate types, references, layers, order positions and resource limits.
2. Resolve local dependencies.
3. Reject missing inputs, invalid ranges, duplicate keys and cycles.
4. Construct new immutable definitions in temporary state.
5. Construct all intermediate stream occurrences and batch records.
6. Publish the complete state transition atomically.
7. Publish nothing when any required validation or construction step fails.

The current CPU implementation performs an in-memory state-pointer replacement. A physical Etabit Drive still needs a separately approved durable contract for:

- mounted location and namespace;
- physical record encoding;
- transactional publication;
- locking and writer ownership;
- crash recovery;
- reload verification;
- compaction without identity loss;
- multi-writer conflict handling;
- storage and traversal limits.

### 11. Document use

Syn-Etabit Transformer — Textual uses Markdown as primary textual content and JSON as the plan that references structure, metadata, assets, transformations and emission requirements.

The JSON plan can reference Etabit maps without embedding every referenced body into one document.

The resulting native state remains distinct from its emitted targets:

```text
Markdown content
      +
JSON document plan
      +
Etabit map references
      +
transformation catalogue
             ↓
resolved document state
             ↓
immutable ejection package
             ↓
external target-format adapter
             ↓
derived artifact and receipt
```

DOCX, PDF and HTML outputs are therefore derived emissions. They do not become the native authority merely because they were rendered.

### 12. CPU, GPU and agentic boundaries

The CPU implementation is the semantic reference model.

A future GPU representation may accelerate map traversal, transformation resolution or rendering only after its address widths, binary representation, deterministic behavior and equivalence checks are defined. The GPU must not silently redefine the CPU semantics.

Agentic control remains the final integration layer. An agent may eventually submit governed requests to the service, but it does not define Etabit identity, bypass validation or become the authority for retained evidence.

### Current proof boundary

The repository currently contains:

- a safe-ASCII native CPU construction model;
- immutable content-addressed assemblies;
- retained stream occurrences and ancestry;
- atomic in-memory batch publication;
- a bounded relative-and-replaceable map probe;
- replayable JSON/JSONL evidence;
- hardening, deterministic fuzzy-error and torture tests.

It does not currently contain a proven live Etabit mount or durable Etabit filesystem.

The Etabit locator, map API, physical encoding, durable atomicity, locking, recovery and multi-writer behavior remain unresolved requirements. This README describes the intended construction contract; it must not be read as evidence that those missing substrate capabilities are already implemented.

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

