# Mining Validation

Date: 2026-10-31. Scope: approved three-archive mining package and bounded local validation.

## Production scope

The user approved the revised proposal with **“yes.”** The clearance covered mining the three supplied archives, the nested inactive UPTI-SF specification, four additional reports, isolated rerunning of supplied local tests, and the stated exclusions. No transport, resolver, Strmdocx runtime, database, parser, codec, sentinel system or protocol integration was implemented.

## Source integrity

| Source | Manifest entries | Failures |
| --- | ---: | ---: |
| Holon Design Handoff | 15 | 0 |
| UPST application payload v0.1 | 13 | 0 |
| UPTI handoff v0.2 candidate | 33 | 0 |
| Nested UPTI-SF historical specification | 9 | 0 |

The three outer archive SHA-256 values match the intake register. The nested UPTI-SF bytes match the digest recorded in UPTI v0.2. These checks establish agreement with the supplied manifests and intake bytes, not authorship or semantic truth.

## Source JSON validation

Thirty JSON files across the extracted Holon handoff, UPST v0.1, UPTI v0.2 and nested UPTI-SF source sets were parsed using a strict standard-library parser that rejected duplicate properties and nonstandard numeric constants.

Result: **30 parsed; 0 failures.**

## Lineage and duplicate validation

- All thirteen external v0.1 nonmanifest files match the v0.2 embedded legacy copies.
- Ten v0.1 files are reused unchanged at the v0.2 root.
- v0.2 root README, test report and TODO differ and are classified as later candidate status documents.
- Duplicate copies were counted once for semantic mining and separately for artifact provenance.

## Supplied test execution

Execution occurred in an isolated system temporary extraction using the available Python standard library. No dependencies were installed and no network or receiver was invoked.

| Suite | Observed result | Exit |
| --- | --- | ---: |
| UPST v0.1 `unittest discover` | 10/10 passed | 0 |
| UPTI v0.2 `unittest discover` | 34/34 passed | 0 |

The v0.2 count includes the unchanged v0.1 tests. Historical nested UPTI-SF claims of 25 integration tests plus fuzzy, torture and crash-oriented testing were not rerun because the historical implementation and full test corpus are absent.

## Mining-output structural checks

Before manifest generation, the two generated JSON catalogs were parsed with duplicate-property and nonstandard-constant rejection.

| Check | Result |
| --- | --- |
| Catalog declared records | 44 |
| Actual catalog records | 44 |
| Unique record identifiers | 44 |
| Related-record references | 120, all resolved |
| Source-register records | 6, all unique |
| Status values | All drawn from declared vocabulary |
| Records with source locators | 44/44 |
| Native JSON null in generated catalogs | None |
| Required pre-validation outputs | Present |

The generated manifest is validated separately after creation.

## Classification checks

- Current direct user decisions are labeled separately from handoff-recorded decisions.
- Assistant inferences and unadopted proposals are labeled as such.
- Candidate local implementations are not labeled canonical.
- Historical and superseded structures are retained without being promoted.
- Historical validation claims are distinguished from current observed test results.
- The v0.1 native-null rule and later sentinel requirement remain an explicit unresolved conflict.
- “Everything is by reference” is retained as controlling while its exact representation remains open.

## Temporary execution material

The isolated extraction used:

```text
<local-user-home>\AppData\Local\Temp\strmdocx-holon-mining-28a64ecd89084e509af27257a0dd4863
```

It is not a project source, output or authority record. The approved mining artifacts reside only in the research destination. No original archive was changed.

An exact-path, prechecked recursive cleanup command was attempted after validation, but the execution policy rejected it before the command ran. The temporary extraction therefore remains at the recorded system-temp path. This is a housekeeping residue containing extracted copies and Python test cache material; it is not included in the output manifest and no result depends on its continued presence.

## Proof limits

This validation does not establish:

- authenticity or authorship of supplied artifacts;
- completeness of historical chats or source packages;
- correctness of absent Holoquary v1.2 material;
- accepted UPTI/UPST protocol conformance;
- network transfer, delivery or receiver acknowledgment;
- authenticated identity, authorization, encryption or signatures;
- independent attestation;
- exhaustive fuzz, torture, crash or security testing;
- semantic equivalence of arbitrary transformations;
- a completed reference, relationship, identity, sentinel or storage design;
- Strmdocx runtime correctness or integration approval.

The package is a provenance-preserving mined design account. It is not an executable specification or production service acceptance.
