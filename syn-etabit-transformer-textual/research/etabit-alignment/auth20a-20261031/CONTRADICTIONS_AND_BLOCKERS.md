# AUTH-20A contradictions and blockers

Date: 2026-10-31 (America/New_York)  
Status: open unless explicitly marked as a reusable boundary

This report separates true contradictions from missing contracts. A contradiction does not mean either project is wrong; it means the two current models cannot be treated as one schema without a governing decision. A blocker means that implementation would require inventing a source, interface or authority.

## Critical blockers

### AB-01 — There is no durable Etabit substrate to target

**Type:** blocker  
**Evidence:** S04, S06, S10–S13, S16, S18  
**Effect:** A persistence probe cannot be written against a real Etabit path or API. AmorphousDrive contains a locked architecture, working direction, a separate registry candidate and review evidence; it does not contain an admitted sf-Etabit storage implementation or listening service.

**Required closure:** approve a paper-level CPU substrate contract defining locator, record envelope, reference grammar, atomic publication, reload, failure, recovery, capacity and proof limits. Only then propose an implementation.

### AB-02 — Storage D0 and registry-preservation D0 are namespace collisions

**Type:** contradiction / namespace hazard  
**Evidence:** S11, S12, S14  
**Effect:** A bare `D0` can mean raw zero-metadata substrate or the first level of a preservation registry. Mapping records by the shared label would silently corrupt the architecture.

**Required closure:** require full names such as `sf-etabit.storage/D0` and `sf-registry.preservation/D0` in schemas, reports and APIs. No unqualified serialized `D0` value.

### AB-03 — Strmdocx construction layers do not have an accepted D1/D2 placement

**Type:** blocker  
**Evidence:** S01–S04, S14  
**Effect:** sf-Etabit D1 permits atoms and molecules, including word stems/endings/words, while D2 explicitly composes words and larger objects. Strmdocx distinguishes glyph, component, root, word, phrase, sentence, paragraph and document. A one-to-one mapping is not stated by either project.

**Required closure:** decide whether `WORD` is a D1 molecule, a D2 composition, or represented at both layers with different identities and an explicit relation. Do the same for every native layer.

### AB-04 — Bitmap membership does not yet encode ordered repeated occurrences

**Type:** blocker  
**Evidence:** S06, S10, S11, S14, S16, S17, S19  
**Effect:** Strmdocx construction and streams depend on exact order and repeated references. Current AmorphousDrive direction explicitly says bitmap ordering, repetition, index semantics and x/y width semantics remain open.

**Required closure:** specify position identity, multiplicity, stable ordering, repeated-reference behavior, bounds, missing positions and reconstruction determinism.

### AB-05 — Identity roles are unresolved

**Type:** blocker  
**Evidence:** S02, S05, S10, S11, S13  
**Effect:** Strmdocx uses content-derived definition/map IDs, model-namespace stream occurrence UUIDs, batch IDs and source locators. sf-UUID is needed but its format, issuance, uniqueness and copy/replacement semantics are open. Treating one existing identifier as sf-UUID would merge distinct roles.

**Required closure:** approve an identity matrix for raw reference, member, content recipe, occurrence, map version, context, source occurrence, derivation and attestation records.

### AB-06 — WordNet bytes cannot simply be labeled D0

**Type:** contradiction  
**Evidence:** S03, S04, S14  
**Effect:** The WordNet tar member, record, token and archive are already ordered file-like structures. Locked D0 contains raw enumerated values and no file, identity, locator, encoding or reconstruction information.

**Required closure:** define how raw substrate values are referenced, how source bytes are reconstructed above D0, and where archive/member/offset/hash provenance lives.

### AB-07 — Replaceable interpretations and locked architecture use different change rules

**Type:** conditional contradiction  
**Evidence:** S01, S05, S06, S10, S14  
**Effect:** Strmdocx says everything is relative and replaceable. sf-Etabit v0.3 says changes that weaken D0 or memory/attestation boundaries require explicit unlock/revision authority. “Replaceable” cannot mean that a context silently changes a locked invariant.

**Required closure:** state that interpretations and composed contexts are replaceable, while a locked baseline is immutable within its identity. A changed baseline receives a new lock and explicit authority.

### AB-08 — Constructor/reader metadata separation is not implemented

**Type:** contradiction  
**Evidence:** S02, S03, S05, S16, S19  
**Effect:** Strmdocx's current local packages expose source and construction evidence in one process. The Decomposition Etabit direction says optional per-drive meta data is constructor-accessible and reader-inaccessible.

**Required closure:** decide whether this separation applies to the first Strmdocx adapter. If it does, define distinct capability surfaces and negative tests, including indirect disclosure. If it does not, do not claim Decomposition Etabit conformance.

### AB-09 — Cypher governance cannot be inferred from the service writer

**Type:** contradiction / authority gap  
**Evidence:** S01, S16, S18, S19  
**Effect:** Strmdocx's proposed SQLite single owner is a serialization mechanism. The Cypher Disk is described as internally distributed authority deciding metadata, association, construction, disclosure and writes. No collective-decision rules exist.

**Required closure:** keep Cypher authority out of the first storage reference model, or obtain direct decisions for constituent identity, refusal, quorum/threshold, audit, compromise, staleness and enforcement. Never rename a single writer as Cypher.

### AB-10 — Holonic refusal has no Strmdocx transaction semantics

**Type:** blocker  
**Evidence:** S16, S19  
**Effect:** A rejected edit, invalid reference and a constituent's refusal/revocation are not the same event. Current Strmdocx errors cannot represent the latter without invention.

**Required closure:** define typed refusal, withdrawal, alternative arrangement, stale consent and atomic-abort behavior before authority-bearing integration.

### AB-11 — Current verification is not sf-Etabit attestation

**Type:** contradiction / proof limit  
**Evidence:** S03, S05, S09, S14–S16, S18  
**Effect:** Hash manifests and replay establish bounded byte identity and deterministic rebuild. Locked v0.3 requires persistent high-friction validation and forbids cached success or memory from reducing validation cost. Neither project has demonstrated cross-project attestation.

**Required closure:** define a deliberately limited reference-validation profile and name it accurately. Full sf-Etabit attestation requires separate persistent evidence, disagreement handling and recovery contracts.

### AB-12 — Grammar, syntax and Government-and-Binding sources are insufficient

**Type:** source blocker  
**Evidence:** S05–S08  
**Effect:** Placeholder mechanical theory replacement has been proven, but no substantive governing theory edition was available. WordNet pointers cannot supply the missing grammar rules.

**Required closure:** designate governing primary sources, mine locators, resolve conflicts, propose schemas, and obtain a separate implementation approval.

### AB-13 — WordNet does not define native roots or affixes

**Type:** source blocker  
**Evidence:** S01, S03, S04, S07, S08  
**Effect:** Recognizable spelling sequences and exception pairs do not authorize roots, prefixes, suffixes or etymology. The meaning-free `marion`/`ette` construction remains a project fixture, not a WordNet derivation.

**Required closure:** use direct curated declarations or a designated construction source with provenance. Literal symbol fallback remains valid.

### AB-14 — Physical full-enumeration language must not leak into Strmdocx claims

**Type:** scope hazard  
**Evidence:** S14  
**Effect:** Locked v0.3 quantifies a complete 64-bit D0 at 128 EiB. Strmdocx's logical IDs and safe-ASCII catalog do not demonstrate or require such a physical substrate.

**Required closure:** state the bounded subset or simulated reference substrate exactly and make no full physical enumeration claim.

### AB-15 — The Decomposition source has a fidelity ceiling

**Type:** evidence blocker  
**Evidence:** S15, S16, S18, S19  
**Effect:** The handoff preserves user messages and often nonverbatim assistant summaries; it is not a certified complete platform export. Historical decisions are useful but cannot settle missing current contracts by implication.

**Required closure:** obtain direct present decisions for any consequential authority, wire, media or security rule.

## Reusable non-conflicting boundaries

- D0 carries no identity, type, codepage, symbol, relation, order, provenance, attestation or reconstruction metadata.
- Order and repeated occurrences must be explicit above D0.
- Construction never grants execution authority.
- Stored marker values are distinct from retrieval and resolution status.
- Prior sources, maps, streams and contexts are preserved.
- Filesystem paths are locators/overlays, not semantic or execution authority.
- Memory and cached success do not replace persistent validation.
- Agentic integration remains last.

## Stop condition

No code, database, Etabit directory, WordNet load, registry admission, Cypher mechanism, GPU representation or agent registration should be produced from this study. The next scope must resolve the minimum decisions and receive its own concrete approval.
