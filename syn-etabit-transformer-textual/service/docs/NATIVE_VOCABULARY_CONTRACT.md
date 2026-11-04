# Native vocabulary pilot contract

Contract date: 2026-10-30 (America/New_York)  
Authorization: AUTH-17  
Status: implemented and locally validated within the bounded pilot

## 1. Purpose and authority

AUTH-17 tests whether selected Princeton WordNet 3.1 word forms can be
represented by the existing `docstream.native.safe-ascii/1` CPU model without
turning WordNet meanings, synsets, exception relations or guessed morphology
into native construction payloads. The governing source is the preserved
`research/wordnet/princeton-3.1/wn3.1.dict.tar.gz` archive with SHA-256
`3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a`.
That digest establishes the bytes used by this project; it is not an external
publisher signature.

The reusable implementation is `docstream_cpu.native_vocabulary`. It creates an
isolated in-memory `NativeModel`, returns immutable source and construction
records, writes retained evidence atomically, and can replay-verify that
evidence. It does not activate the document service or install a dependency.

## 2. Approved ceilings

| Item | Ceiling |
| --- | ---: |
| Selected data-file form occurrences | 1,000 total; at most 250 each from noun, verb, adjective and adverb |
| Exception form/base pairs | Up to 100 total; at most 25 from each part of speech |
| Selected source bytes | 8,388,608 |
| Source records examined | 10,000 |
| Pilot execution time | 600 seconds |
| Peak process working set | 536,870,912 bytes |
| Native definitions | Existing model ceiling of 4,096; not expanded by AUTH-17 |

`up to` is important for exception relations. A source member may contain fewer
eligible pairs than its cap. Natural end-of-file is a complete examination of
that member. `PARTIAL` is reserved for a quota left incomplete because the
approved byte or record budget was exhausted.

## 3. Source reading and retained provenance

The reader opens only these named tar members and never extracts the archive:

- `dict/data.noun`, `dict/data.verb`, `dict/data.adj`, `dict/data.adv`
- `dict/noun.exc`, `dict/verb.exc`, `dict/adj.exc`, `dict/adv.exc`

Every selected form retains part of speech, synset offset, synset type, word
position, raw word token, decoded form, lexical ID, optional adjective syntax
marker, member name, one-based line number, zero-based member byte offset and
the SHA-256 of the raw source line. Every selected exception pair retains both
forms, base position and the same locator structure. Duplicate source
occurrences remain separate records even when their native definition is
shared.

The data-file hexadecimal word count is parsed according to the WNDB record
layout. `(p)`, `(a)` and `(ip)` suffixes are separated into provenance fields;
they are not emitted as word characters. WordNet collocations containing `_`
are counted and excluded in this pilot. The implementation does not guess
whether an underscore should become a space, remain an underscore, or map to a
future multiword layer. Non-ASCII source text is rejected rather than
transliterated.

Glosses, pointer fields, synset meanings and lexical relations are not loaded
into native payloads. Exception pairs are retained as external source
relations, not executed as suffix-removal rules.

## 4. Explicit fragment registry

The registry adapts only structures established before AUTH-17:

| Native layer | Exact byte text | Construction |
| --- | --- | --- |
| glyph | `un`, `he`, `an`, `et`, `te`, `er`, `nd` | Literal safe-ASCII symbols |
| component | `ette` | glyph `et` followed by glyph `te` |
| component | `-ette` | literal hyphen followed by glyph `et` and glyph `te` |
| component | `un` | glyph `un` unchanged |
| component | `er` | glyph `er` unchanged |

Labels and matching metadata live outside native definitions. Neither a label
nor spelling assigns a linguistic meaning. In particular, `-ette` is a distinct
ordered construction containing byte 45; the hyphen is not an operator.

## 5. Deterministic word construction

Construction is exact and case-sensitive. At each byte position the builder
chooses the longest matching explicit fragment. A tie selects the higher
already-established native layer and then the lexically first stable fragment
ID. If nothing matches, exactly one `SymbolRef` is emitted for that byte. A
`WORD` definition contains the resulting ordered references.

The algorithm is a reproducibility rule, not a morphology or etymology claim.
No roots are inferred. A word may directly reference symbols, glyphs and
components because the native contract permits lower-layer references and
unused layers may be skipped. Identical constructions share content-addressed
definitions; every source occurrence and exception relationship remains
separately addressable outside the native payload.

## 6. Errors and publication

Errors have stable codes including `SOURCE_NOT_FOUND`, `SOURCE_HASH_MISMATCH`,
`MALFORMED_ARCHIVE`, `MISSING_SOURCE_MEMBER`, `MALFORMED_SOURCE`,
`SOURCE_LINE_LIMIT`, `OUTPUT_EXISTS`, `EVIDENCE_HASH_MISMATCH`,
`REPLAY_MISMATCH` and `EXPANSION_MISMATCH`. Type and ceiling violations use
`VALIDATION_ERROR`.

Source parsing and validation finish before the isolated `NativeModel` is
created. No caller-owned model is accepted, so a malformed source cannot leak a
partially populated caller catalog. Evidence is written to a fresh temporary
directory and renamed only after all payloads and their manifest exist. An
existing destination is never overwritten. Verification checks the exact file
set and hashes, rebuilds from the approved archive, compares deterministic
payload bytes and expands every retained native word reference.

## 7. Evidence interface

From the `service` directory:

```powershell
.\.venv\Scripts\python.exe -m docstream_cpu.native_vocabulary `
  --source ..\research\wordnet\princeton-3.1\wn3.1.dict.tar.gz `
  --output ..\.docstream\native-vocabulary-runs\auth17-20261030-final

.\.venv\Scripts\python.exe -m docstream_cpu.native_vocabulary --verify `
  --source ..\research\wordnet\princeton-3.1\wn3.1.dict.tar.gz `
  --output ..\.docstream\native-vocabulary-runs\auth17-20261030-final
```

The retained run contains `result.json`, `forms.jsonl`, `exceptions.jsonl`,
`fragments.json`, `constructions.jsonl` and `manifest.json`.

## 8. Explicit exclusions

AUTH-17 does not authorize or claim complete WordNet absorption, a durable
native vocabulary database, inferred roots or affixes, semantic payloads,
collocation conversion, Unicode/CP437 expansion, service/MCP activation,
renderer or DOCX behavior, capacity changes, GPU lowering, release, or
agentic-control integration. Agentic-control integration remains last.
