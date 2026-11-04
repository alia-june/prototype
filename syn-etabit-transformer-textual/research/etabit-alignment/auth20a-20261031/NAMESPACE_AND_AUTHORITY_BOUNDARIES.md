# Namespace and authority boundaries

Date: 2026-10-31 (America/New_York)  
Authorization: AUTH-20A

## Terminology correction

The user clarified on 2026-10-31 that `edabit` was a typo and the current term is **Etabit**. Derived prose and derived namespace labels therefore use **Etabit / sf-Etabit**. Exact source paths, filenames and serialized identifiers containing `edabit` or `sf_edabit` remain unchanged as literal locators or legacy identifiers; they do not establish a separate architecture or valid alternate current spelling.

## 1. Required namespace qualification

| Qualified namespace | Meaning | Present status | Must not be confused with |
| --- | --- | --- | --- |
| `sf-etabit.storage/D0` | Raw ordered enumerated values; zero metadata and zero self-description | Locked v0.3 architecture | Files, archive records, registry preservation D0, Strmdocx symbols |
| `sf-etabit.storage/D1` | Relation and interpretation of D0; datatypes, encodings, codepages, symbols, tuples, bitmaps, atoms/molecules | Locked v0.3 architecture | Strmdocx `Layer.COMPONENT`, service database tables, registry D1 |
| `sf-etabit.storage/D2` | Ordered composition and coherent reconstruction from D1 | Locked v0.3 architecture | Strmdocx stream ordinal, registry D2, filesystem |
| `sf-etabit.attestation` | Persistent validation above D2, with optional nonauthoritative memory witness | Locked v0.3 architecture; no demonstrated implementation | Hash manifest alone, in-memory cache, local test pass |
| `sf-registry.preservation/D0–D5` | Preservation-depth wire namespace in the registry candidate | Separate candidate namespace; admission blocked | sf-Etabit storage D0/D1/D2 |
| `strmdocx.native/Layer` | GLYPH, COMPONENT, ROOT, WORD, PHRASE, SENTENCE, PARAGRAPH, DOCUMENT | Implemented in-memory CPU reference profile | sf-Etabit storage layers |
| `strmdocx.relative-map/kind` | Objects, orders, structures, processes, grammar, syntax, theory, relations, contexts and ledgers | Implemented bounded mechanical probe | Physical drives or admitted Etabit maps |
| `decomposition.etabit/concept` | Source and referential multi-drive research model, optional constructor-only metadata, Cypher governance and refusal | Source-qualified research | Locked sf-Etabit v0.3 or a runtime implementation |

**Rule:** serialized data and APIs should use full namespace and profile identifiers. Human shorthand may be used only after the document establishes which namespace governs the section.

## 2. Identity boundaries

| Identity | Current meaning | Authority ceiling |
| --- | --- | --- |
| Native definition ID | SHA-256 of canonical Strmdocx native definition payload | Content/recipe identity only |
| Relative map ID | SHA-256 of canonical map kind, version, context, inputs and entries | Map recipe identity only |
| Stream ID | Model-namespace UUID plus local ordinal | In-memory occurrence identity; not durable cross-process identity |
| Source occurrence locator | Archive/member/line/offset/hash tuple | Evidence locator, not substrate member identity |
| sf-UUID | Needed for members in current AmorphousDrive direction | Format, issuance and uniqueness unresolved |
| Drive UUID | Optional and discouraged in current direction | Must not be required by inference |
| Handoff ID | Descriptive local identifier in the Decomposition package | Not a canonical Bitcore, sf-ObjectID or sf-UUID code |
| SHA-256 | Byte or canonical-payload digest | Proves identity of hashed bytes/payload only; not authorship, authority or truth |

No conversion between these identities is implied. Any later adapter must preserve the source identity and record the new identity plus derivation, never relabel an existing digest.

## 3. Layer and record boundaries

### D0 exclusions

The following Strmdocx information cannot be stored *as D0 metadata*:

- symbol/codepage/type labels;
- assembly layer;
- child references;
- definition IDs;
- stream, batch or operation IDs;
- WordNet archive/member/line/offset/hash locators;
- order maps;
- grammar, syntax or theory maps;
- source, derivation or replacement ledgers;
- validation or attestation records.

These records may refer to raw positions from above D0 after an approved placement contract. Nothing in AUTH-20A defines the physical or logical encoding of those references.

### D1 candidates

- explicit datatype, encoding and codepage definitions;
- safe-ASCII symbol interpretation;
- typed relations to raw positions;
- reusable atoms and molecules;
- source relation symbols and exact pointer fields;
- qualified relation bitmaps.

The placement of glyph/component/root/word is not adopted. The locked baseline supplies examples, not a complete Strmdocx mapping.

### D2 candidates

- ordered occurrences;
- words if defined as compositions rather than D1 molecules;
- phrases, sentences, paragraphs and documents;
- source file/archive reconstruction;
- alternate composition paths and retained stream results.

Equivalence between two compositions requires evidence and deterministic selection. Equal expanded bytes alone need not mean equal structural identity.

### External or later overlays

- filesystem paths and filenames;
- ownership, rights, permissions and policy;
- service tokens and agent credentials;
- human labels and UI state;
- release and deployment configuration.

Provenance and attestation are external to D0 but need a separate approved placement decision; this study does not force them into a generic metadata overlay.

## 4. Authority boundaries

| Actor or record | May establish | May not establish |
| --- | --- | --- |
| Strmdocx user decision | Project direction and approved scoped work | sf-Etabit implementation existence or independent attestation |
| Locked sf-Etabit v0.3 | Baseline D0/D1/D2 and attestation invariants | A current path, API, physical device, registry admission or Strmdocx mapping |
| AmorphousDrive working direction | Current unresolved direction | New lock, sf-UUID format or storage topology |
| Decomposition handoff | Source-qualified decisions, corrections and open contracts | Runtime authority, security proof, quorum or wire format |
| Native/relative-map tests | Bounded local behavior of the tested CPU models | Etabit persistence, linguistic correctness, production capacity or security |
| Registry candidate | Candidate operation/preservation behavior within its tests | sf-Etabit storage, admission, controller authority or deployment |
| Hash/manifest | Byte or payload identity and listed-set consistency | Authenticity, completeness, semantics, permission or current validity |
| Memory/cache | Secondary observation or witness | Canonical recovery, skipped validation or final fallback |
| Valid construction | A reconstructable representation under its profile | Permission to execute, disclose or write |

## 5. Constructor, reader and governance

The Decomposition Etabit material distinguishes:

- source/reference data;
- optional out-of-band metadata accessible to an authorized constructor;
- a reader with no direct metadata access;
- internally distributed Cypher authority;
- constituents capable of refusal or revocation.

Strmdocx currently has no accepted capability matrix implementing those roles. Until one is approved and tested:

1. do not call the service process a constructor with Cypher authority;
2. do not call ordinary catalog access a reader-isolated interface;
3. do not encode a single-writer decision as distributed consent;
4. do not treat a validation failure as holonic refusal;
5. do not infer permission to disclose source metadata from the ability to reconstruct text.

## 6. Change and replacement

Replacement in Strmdocx means a new immutable context or successor retaining prior identities and evidence. Change control in locked sf-Etabit means an architectural deviation requires explicit unlock/revision authority. These rules are compatible only under this boundary:

```text
replace interpretation or context
    -> new qualified identity; prior state retained

change locked D0/D1/D2 invariant
    -> not an ordinary replacement
    -> explicit revision authority and new locked baseline required
```

## 7. Result typing

At minimum, a later interface must keep these domains disjoint:

```text
stored_value
read_result
reference_resolution
validation_result
authority_result
cooperation_result
attestation_result
```

A stored `Error` symbol is not a read failure. A stored `Unknown` symbol is not an unresolved reference. An unresolved reference is not a lack of authority. A lack of authority is not constituent refusal. A refusal is not corruption. This separation is a reusable design safeguard, not an adopted four-valued algebra.

## 8. Current conclusion

The projects can share a disciplined reference model, but they do not yet share an implementation namespace or authority system. The first safe integration artifact must be an approved placement/identity/occurrence contract. Only after that contract exists should a bounded CPU storage reference implementation be proposed.
