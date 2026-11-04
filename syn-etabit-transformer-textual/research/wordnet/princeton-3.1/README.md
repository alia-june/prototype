# Princeton WordNet 3.1 source acquisition

Acquired 2026-10-30 following the user's direct instruction: "no better download
it yourself". That instruction authorized source acquisition only. The user
subsequently and separately approved AUTH-17, a bounded native vocabulary pilot;
its completion does not authorize full-corpus population or service activation.

- Official publisher archive: https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz
- Local archive: wn3.1.dict.tar.gz
- Bytes: 16,358,468
- SHA-256: 3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a
- Embedded release: WordNet 3.1, copyright 2011 Princeton University.
- Verification: complete gzip read/CRC check passed; uncompressed tar length
  55,128,576 bytes; 69 archive members inventoried without bulk extraction.
- Detailed receipt, member metadata and small source samples: SOURCE_MANIFEST.json.
- Exact numbered licence header copied from dict/index.noun:
  LICENSE.source-header.txt. Original notices also remain inside the archive.

No independent publisher checksum/signature was verified. The hash identifies
the retrieved bytes; it does not establish authority beyond the stated source
and observations. No bundled programs were executed or dependencies installed.

## Bounded application status

Use WordNet as a source of candidate spellings and separately catalogued form
relations. The native construction payload remains ordered references with no
embedded definitions, synonym sets or linguistic behavior. WordNet's Morphy
rules/exception pairs map forms toward database base forms; they do not provide
the complete glyph/component/root construction required by this project.

Princeton's WNDB documentation distinguishes lower-case index lemmas from
case-sensitive data-file word forms. It also defines underscore encoding for
collocations and adjective syntactic markers. Preserve raw source fields and
locators before any explicitly approved decoding. Do not silently lowercase,
convert punctuation, infer roots or equate equal spellings with equal senses.

Sources reviewed:

- https://wordnet.princeton.edu/documentation/wndb5wn
- https://wordnet.princeton.edu/documentation/morphy7wn
- https://wordnet.princeton.edu/documentation/wninput5wn
- The actual 3.1 numbered licence header and a small index/exception sample.

AUTH-17 completed a bounded application using the data and exception members:
1,000 balanced form occurrences, 82 eligible exception pairs, 1,082 locators,
1,003 unique word constructions and 11 explicit fragments. The run used 1,014
of the current 4,096-definition budget. Exact rules, validation and findings are
recorded in `service/docs/NATIVE_VOCABULARY_CONTRACT.md`,
`NATIVE_VOCABULARY_VALIDATION.md` and `NATIVE_VOCABULARY_FINDINGS.md`.

Literal symbol fallback remains available for AI-generated strings absent from
the vocabulary. Non-ASCII entries are not transliterated into the safe profile.
Full absorption, inferred roots, collocation conversion, durable persistence,
GPU and agentic-control integration remain later scopes requiring separate
approval.
