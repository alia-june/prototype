# Strmdocx ↔ sf-Etabit crosswalk

Date: 2026-10-31 (America/New_York)  
Authorization: AUTH-20A  
Result: **alignment is conceptually useful, but durable integration is blocked by unresolved namespace, placement, identity, authority and storage contracts.**

## Executive determination

Strmdocx and sf-Etabit share several principles: interpretation is separate from raw values; order is identity-bearing; larger structures are assembled through explicit references; prior structures remain addressable; construction does not grant execution authority; and source evidence must not be overwritten by later interpretations.

That agreement is not yet an implementation map. sf-Etabit v0.3 is a locked architectural baseline, not a mounted store. AmorphousDrive has no admitted storage implementation. Strmdocx has an in-memory native catalog, retained evidence packets, and a passing bounded product test, but no durable native vocabulary catalog or Etabit adapter. A live persistence probe would therefore test an invented interface.

The critical distinction is:

```text
sf-Etabit storage D0/D1/D2
    ≠ registry-preservation D0–D5
    ≠ Strmdocx native Layer enum
    ≠ Strmdocx relative-map kinds
```

These systems may be cross-referenced only through qualified mappings. No numeric or textual name is equivalent by coincidence.

## Classification key

| Classification | Meaning |
| --- | --- |
| `compatible` | The sources express the same governing constraint closely enough to reuse as a boundary. |
| `candidate` | A plausible mapping exists, but adoption requires a decision or a new scoped specification. |
| `conflict` | Current models make materially different commitments. Neither silently overrides the other. |
| `blocked` | A required contract, source, API or authority is missing. |
| `unrelated` | The topic is outside the other source's present scope. |
| `historical` | Useful lineage or correction only; not current implementation authority. |

## Crosswalk summary

| ID | Topic | Classification | Determination |
| --- | --- | --- | --- |
| CW-001 | Raw value vs interpretation | compatible | sf-Etabit puts interpretation above D0; Strmdocx keeps meaning/provenance outside native construction payloads. |
| CW-002 | Safe-ASCII symbols | candidate | Strmdocx symbol values and codepage identity fit D1, not D0. The profile is a test repertoire, not sf-Etabit canon. |
| CW-003 | Codepages | compatible | Both require explicit codepage identity and reject inference from raw values alone. |
| CW-004 | Direct references | candidate | Native references can inform D1/D2 recipes, but their Python objects and definition IDs are not sf-Etabit addresses. |
| CW-005 | Glyph/component/root/word layers | blocked | sf-Etabit permits D1 atoms/molecules and D2 words, creating an unresolved boundary for Strmdocx `WORD` and lower construction layers. |
| CW-006 | Order | compatible | Both make order explicit and identity-bearing; a bitmap that records membership alone is insufficient. |
| CW-007 | Sentences/paragraphs/documents | compatible | These are clear D2 composition candidates, subject to identity and reconstruction contracts. |
| CW-008 | Content-addressed map identity | candidate | Useful for recipes and evidence, but not a substitute for the unresolved sf-UUID. |
| CW-009 | Contextual replacement | candidate | Strmdocx replacement can coexist with locked baselines if replacement creates a new context/version and never silently edits the lock. |
| CW-010 | Native payload on D0 | conflict | A native assembly payload contains layer and reference structure; locked D0 prohibits all of those fields. |
| CW-011 | WordNet source bytes | blocked | A file/archive is reconstructed structure, not automatically D0. Exact raw-value placement and external locators remain undefined. |
| CW-012 | WordNet semantics | compatible | Source records, lexical relations and construction definitions remain separate. |
| CW-013 | Provenance and derivation | compatible | Both require these outside D0; exact overlay/attestation placement is unresolved. |
| CW-014 | Existing SQLite owner | unrelated | It is a Strmdocx service default, not an sf-Etabit storage implementation or Cypher authority. |
| CW-015 | Multi-map relative composition | compatible | Strmdocx's immutable maps match the multi-drive/referential direction at a conceptual level only. |
| CW-016 | Durable Etabit publication | blocked | No live Etabit path, storage API, transaction protocol, locking or recovery interface exists. |
| CW-017 | D0 naming | conflict | Storage D0 and registry-preservation D0 are separate namespaces and must never be merged. |
| CW-018 | sf-UUID vs map/stream IDs | blocked | Issuance, uniqueness, copying, replacement and duplicate semantics are unresolved. |
| CW-019 | Bitmap occurrence semantics | blocked | Ordering, repetition, index mapping and widths remain open in AmorphousDrive and the Decomposition handoff. |
| CW-020 | Constructor/reader separation | conflict | Current Strmdocx components do not implement a capability boundary preventing readers from accessing construction metadata. |
| CW-021 | Cypher authority | conflict | Distributed Cypher decision authority cannot be represented by the present single SQLite owner without an explicit, limited adapter contract. |
| CW-022 | Holonic refusal | blocked | Strmdocx error and transformation models lack accepted cooperation/refusal/revocation semantics. |
| CW-023 | Four-symbol source example | unrelated | `{1,0,Error,Unknown}` is an optional Etabit source example, not a required alphabet for Strmdocx. |
| CW-024 | Stored symbols vs read status | compatible | In-band values must remain distinct from transport failure and unresolved-reference status. |
| CW-025 | Construction vs execution | compatible | Both prohibit treating a valid structure as permission to execute it. |
| CW-026 | Control characters | compatible | Strmdocx preserves ASCII controls as literal data and does not execute them. |
| CW-027 | Visual rendering | unrelated | Strmdocx requires inspectable rendering; sf-Etabit v0.3 does not define a renderer. |
| CW-028 | Alternative stacks and streams | candidate | Prior immutable streams and alternate D2 stacks can coexist, but equivalence and deterministic selection need contracts. |
| CW-029 | Branch history | compatible | Neither contextual replacement nor new streams requires destructive mutation. |
| CW-030 | Attestation | conflict | Current hashes/replay are bounded evidence; they do not implement v0.3 high-friction persistent revalidation. |
| CW-031 | Memory authority | compatible | In-memory catalogs and cached observations cannot become durable canonical truth. |
| CW-032 | Safe-ASCII scope | historical | The 128-position repertoire is a test increment and must not become a universal codepage assignment. |
| CW-033 | GPU lowering | unrelated | Both bodies of work require CPU/paper correctness first; neither current scope specifies GPU encoding. |
| CW-034 | Agentic integration | compatible | Strmdocx explicitly places agentic integration last; no source provides present authorization to activate it. |
| CW-035 | WordNet map family | blocked | Source-faithful, decoded, constructed, inferred and enriched maps need explicit storage-layer and derivation placement. |
| CW-036 | Grammar/syntax/theory | blocked | No substantive governing Government-and-Binding source or adopted relation decoder exists. |
| CW-037 | Roots and affixes | blocked | WordNet does not authorize the project's meaning-free root/component construction. |
| CW-038 | Files | compatible | sf-Etabit treats files as reconstructed D2 objects; Strmdocx must preserve source byte identity without calling the file a D0 object. |
| CW-039 | Filesystem | compatible | Paths and files are external locators/overlays, not proof of substrate identity or authority. |
| CW-040 | Full 64-bit D0 | unrelated | Strmdocx makes no physical full-enumeration claim and must not inherit one by reference. |

## Reusable boundaries

The following may be reused now as design constraints without claiming storage integration:

1. Qualify every namespace, map identity, version and context.
2. Keep literal/source evidence separate from decoded, composed and inferred records.
3. Make order and repeated occurrence explicit.
4. Preserve old definitions, streams, contexts and source locators.
5. Never place identity, codepage, relation, provenance, attestation or reconstruction information on sf-Etabit D0.
6. Never infer execution authority from reconstruction.
7. Keep stored marker values separate from read, resolution and authorization status.
8. Treat memory and cached success as witnesses only, never as durable authority.

## What must not be adopted wholesale

- The locked sf-Etabit baseline is not a drop-in storage schema for the current Python native model.
- The Decomposition handoff's A/B/C illustration is not a mandatory topology.
- The four-symbol example is not Strmdocx's alphabet or failure model.
- The Cypher Disk is not the current SQLite writer, and no quorum may be invented.
- D1 `molecule` examples do not settle where Strmdocx words belong.
- A hash ID does not settle sf-UUID.
- A retained JSON/JSONL packet is not Etabit persistence.
- Passing Strmdocx tests do not attest sf-Etabit conformance.

## Recommended next move

Do not implement a storage adapter yet. First resolve the minimum decisions in `MINIMUM_INTEGRATION_DECISIONS.md`, beginning with the qualified namespace dictionary, the D1/D2 placement of each Strmdocx record type, ordered occurrence semantics, and identity roles. After those decisions are approved, a later proposal can specify one CPU-only, read/write/reload substrate reference model without WordNet bulk load, Cypher governance, GPU work or agentic activation.
