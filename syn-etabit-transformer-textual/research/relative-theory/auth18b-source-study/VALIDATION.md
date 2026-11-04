# AUTH-18B validation

Date: 2026-10-30 (America/New_York).

## Study result

The packet contains 10 registered sources, 16 WordNet relation/structure records, 17 proposed generic relations, 11 grammar/syntax/theory or gap records, 10 crosswalk records and 13 AUTH-18A sample records: 77 globally addressable records across six hash-pinned JSON catalogs.

The strict inspector reports:

```text
status: PASS
files: 6
records: 77
catalog bytes: 32,598
study status: PARTIAL_GOVERNING_SOURCE_MISSING
```

Every structured reference resolves. Source-defined WordNet records and proposed project records retain different statuses. No Government-and-Binding formal relation was created.

## Focused validation

`python -m unittest service.tests.test_theory_inspector -v` passed 16 methods in 0.601 seconds. Coverage includes:

- exact schema, hash, size, count and reference checks;
- root containment, duplicate-key and duplicate-record rejection;
- forbidden executable-field rejection;
- exact result, record, byte and trace ceilings;
- 120 seeded invalid-query rejections with exact error codes;
- 200 arbitrary search strings;
- 500 repeated full-query/trace cycles with no packet changes;
- explicit trace-link truncation;
- CLI JSON output and unchanged study hashes.

## Browser validation

The self-contained dashboard was loaded through the project-managed Chromium 1248 executable with network-background features disabled.

| Viewport | Records | Page errors | Body width | Result |
| --- | ---: | ---: | ---: | --- |
| 1440×900 | 77 | 0 | 1440 | PASS |
| 360×800 | 77 | 0 | 360 | PASS |

Screenshots are retained under `.docstream/auth18b-inspector-visual/`. The minimum layout stacks controls, records and detail; neither view has horizontal overflow.

## Project regression result

The complete discovery run executed 267 tests in 55.295 seconds: 265 passed and two pre-existing Windows supervisor/cleanup tests errored. One summary lacked `owned_worker_stopped`; one child retained `child.log` during temporary-directory deletion. Both exact tests passed immediately when rerun separately (one method each). This is reported as **full-suite FAILED; isolated reproductions PASS**, not erased or recast as a full-suite pass. AUTH-18B did not modify either harness.

## Proof boundary

This is local implementation and visual validation. It does not prove linguistic correctness, Government-and-Binding completeness, source authorship, independent attestation, production capacity, live Etabit compatibility or agentic integration.
