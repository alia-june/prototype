# AUTH-20A validation

Date: 2026-10-31 (America/New_York)  
Authorization: AUTH-20A  
Validation status: **PASS** within the stated proof boundary

## Approved bounds

| Bound | Approved | Actual |
| --- | ---: | ---: |
| Source records | at most 20 | 19 |
| Crosswalk records | at most 200 | 40 |
| Short excerpts | at most 30 | 0 verbatim excerpts used as evidence records |
| Output artifacts | exactly 9 | 9 after manifest generation |
| Archive extraction | prohibited | none |
| Dependency installation | prohibited | none |
| Process/service launch | prohibited | none |
| AmorphousDrive writes | prohibited | none by AUTH-20A tools |
| Product-code writes | prohibited | none by AUTH-20A tools |

## Structural checks

The final validation checks:

1. exactly the nine approved filenames exist;
2. all three JSON files parse;
3. source register declares 19 unique IDs and 19 sources;
4. all 19 source bytes/hashes still match the records read;
5. all five ZIP member bytes/hashes still match without extraction;
6. the crosswalk declares 40 unique IDs and uses only the six approved classifications;
7. every crosswalk source reference resolves to a registered source ID;
8. classification counts equal the actual records;
9. no crosswalk record is presented as adopted canon;
10. `SOURCE_MANIFEST.json` covers the other eight approved artifacts and excludes itself to avoid a recursive hash;
11. no file was created in AmorphousDrive;
12. no Strmdocx product file was changed by the bounded artifact-production actions.

## Workspace preservation method and limit

The Strmdocx workspace contained 70,492 files and about 1.37 GB before output creation; AmorphousDrive contained 2,936 files and about 46.0 MB. A whole-workspace byte hash was not produced because it would exceed the proportional scope of this nine-artifact study. Preservation is established by:

- exact before/after SHA-256 checks of all 19 registered source records;
- exact before/after archive and ZIP-member checks;
- an exact inventory of the approved output directory;
- the fact that content writes were made only through patches targeting the approved output directory;
- a post-run search for files modified during the production interval outside the approved output root, with any result required to be disclosed rather than ignored.

This proves preservation only to that stated boundary. It is not a filesystem journal, hostile concurrent-writer monitor or independent attestation.

## Semantic review checks

- Every use of D0/D1/D2 is qualified or locally scoped.
- Storage D0/D1/D2 is explicitly separated from registry-preservation D0–D5.
- Locked v0.3 is not rewritten or treated as replaceable by ordinary context selection.
- The Decomposition handoff is not treated as a runtime or security proof.
- The existing SQLite owner is not called Cypher authority.
- Native hash IDs are not relabeled as sf-UUID.
- Files and WordNet archives are not called D0 objects.
- D1/D2 placement of words remains unresolved.
- Constructor/reader separation, holonic refusal and Cypher governance remain unresolved.
- Agentic integration remains last.

## Final executed results

- The two JSON data artifacts and source register parsed successfully before manifest generation.
- Source IDs: 19 declared, 19 present, 19 unique.
- Crosswalk IDs: 40 declared, 40 present, 40 unique.
- Classification counts matched the records: 15 compatible, 5 candidate, 5 conflict, 9 blocked, 5 unrelated and 1 historical.
- Every source reference in every crosswalk record resolved to S01–S19.
- All 14 local source files matched their registered byte counts and SHA-256 values after artifact production.
- The supplied ZIP matched its registered SHA-256, and all five read members matched their registered byte counts and SHA-256 values after artifact production.
- No file outside the approved output directory in the Strmdocx workspace had a modification time at or after the first AUTH-20A artifact creation time, `2026-10-31T22:19:02.9279764Z`, when checked after the eight peer artifacts were complete.
- No file in the AmorphousDrive workspace had a modification time at or after that production-start time.
- `SOURCE_MANIFEST.json` was generated last from the final eight peer artifacts and is intentionally self-excluding.

The final output directory contains exactly the nine approved filenames. The final SHA-256 of `SOURCE_MANIFEST.json` is reported in the user-facing delivery summary because a manifest cannot include its own digest without a recursive definition.

## Proof ceiling

AUTH-20A validates a source-grounded crosswalk and its artifact integrity. It does not validate an Etabit storage API, sf-UUID, physical medium, registry admission, persistent attestation, grammar decoder, WordNet transmigration, GPU representation, service integration, release or agentic control.

## AUTH-20A-C1 terminology correction

The user approved AUTH-20A-C1 on 2026-10-31 to normalize current derived terminology while preserving exact source paths, output filenames and serialized identifiers. The correction did not change crosswalk classifications, source identities, architectural findings or integration recommendations.

Executed correction checks:

- all nine approved output filenames remain present;
- all three JSON artifacts parse;
- 19 source records and 40 crosswalk records remain present and unique;
- all crosswalk source references still resolve;
- all classification counts remain unchanged;
- all 14 local sources, the supplied archive and all five selected ZIP members still match their registered byte counts and SHA-256 values;
- no obsolete hyphenated spelling remains in derived prose or derived namespace labels;
- 49 occurrences remain only in literal source locators, approved output filenames, legacy serialized field names and the single explicit terminology note;
- zero files outside the approved output directory in Strmdocx had modification times at or after the correction start, `2026-10-31T22:29:51Z`;
- zero files in AmorphousDrive had modification times at or after that correction start;
- no source file, product code, registry record, storage state or locked baseline was changed.

`SOURCE_MANIFEST.json` was regenerated after the correction and is again self-excluding. Its final SHA-256 is reported in the delivery summary.
