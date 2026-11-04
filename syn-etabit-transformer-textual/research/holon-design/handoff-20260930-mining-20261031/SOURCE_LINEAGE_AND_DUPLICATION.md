# Source Lineage and Duplication

## Artifact lineage

```text
UPST v0.1 external archive
    ├── preserved byte-for-byte inside UPTI v0.2 /legacy/
    └── selected files reused unchanged at UPTI v0.2 root

UPTI v0.2 root
    ├── corrected current spelling/status documents
    ├── unchanged v0.1 payload contract and validator
    ├── new local staging candidate and tests
    └── nested inactive UPTI-SF specification export
```

## External v0.1 versus embedded legacy copy

All thirteen nonmanifest files in the external v0.1 package match the corresponding files under v0.2 `legacy/holoquary_upst_payload_v0_1/` by SHA-256:

- README
- contract, handoff map, test report and TODO
- five JSON examples
- payload validator
- schema
- payload tests

The v0.1 manifest is not duplicated in the legacy subtree, so archive-level package identity remains separate.

## External v0.1 versus v0.2 root

Unchanged at the v0.2 root:

- `docs/CONTRACT.md`
- `docs/HANDOFF_MAP.md`
- all five v0.1 JSON examples
- `payload.py`
- `schema.json`
- `tests/test_payload.py`

Changed/superseding top-level descriptions:

- `README.md`
- `docs/TEST_REPORT.md`
- `docs/TODO.md`

New v0.2 material:

- `docs/AI_ERROR_LOG.md`
- `docs/UPTI_BOUNDARY.md`
- `staging.py`
- `tests/test_staging.py`
- `examples/demo_handoff.py`
- `reference/SOURCE_INPUT_DIGESTS.json`
- nested inactive UPTI-SF export

## Semantic counting rule

The v0.1 semantic contract is mined once. Each physical copy remains registered for provenance and byte preservation. A repeated byte-identical document does not become independent corroboration merely because it appears in another archive path.

## Terminology lineage

The external v0.1 and embedded legacy copy use **UPST**. The v0.2 top-level documentation corrects the term to **UPTI** and states that the old spelling is historical, not a separate protocol. Historical paths and quotations retain the original spelling.

## Referenced but absent sources

`SOURCE_INPUT_DIGESTS.json` names:

- the supplied v0.1 archive, independently matched by SHA-256;
- the nested UPTI-SF export, independently matched inside v0.2;
- `holoquary_separated_v1_2_source.zip`, not bundled in the supplied sources.

The recorded v1.2 digest is retained as a claim. Its content, completeness and byte identity were not verified.

## Duplicate-analysis proof boundary

This comparison establishes byte equality for named entries. It does not establish common authorship, independent approval, semantic correctness or current adoption. The v0.2 candidate's preservation claims are supported for the compared files; its broader architecture claims retain their stated candidate status.
