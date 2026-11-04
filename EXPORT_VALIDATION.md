# Repository Export Validation

Date: 2026-11-04

Repository destination: `alia-june/prototype`

Project path: `syn-etabit-transformer-textual/`

## Proof boundary

This record reports local export and compatibility checks. It does not claim
deployment, production readiness, independent attestation, current third-party
availability, or activation of any integration.

The source workspace was not modified. Existing source-side Python and browser
resources were used only to execute bounded compatibility tests. They were not
copied into the repository export.

## Clean export checks

The pre-record export contained 311 files and 3,244,211 bytes. The validation
record and export manifest are additional repository evidence files.

The sealed export check found:

- zero `.docstream`, `.venv`, `.browsers`, or `__pycache__` directories;
- zero `.pyc` or `.pyo` files;
- no WordNet dictionary archive;
- no unclassified mosaic image;
- no directory junctions or other reparse points;
- zero matches for the source username, absolute `C:\Users\...` paths,
  `I:\...` paths, Outlook/Gmail addresses, private-key headers, GitHub token
  prefixes, or AWS access-key patterns;
- 57 JSON files parsed successfully;
- 2 TOML files parsed successfully; and
- 99 Markdown files with zero unresolved relative links.

These scans are bounded pattern checks, not a guarantee that no sensitive or
licensed material exists.

## Service suite: payload-free negative control

Command shape: `python -m unittest discover -s tests -v`

The first run used the exported service without the excluded project-local
Chromium tree or historical visual-example SQLite fixture.

- 276 tests ran in 60.601 seconds.
- 259 passed.
- 12 failed and 5 errored.
- Every recorded failure traced to `RENDER_UNAVAILABLE` or the absent
  `visual-example/state.sqlite3` prerequisite.
- The run confirmed that those excluded resources are not silently bundled or
  auto-acquired.

This is retained as a negative-control result. It is not represented as a
passing standalone rendering qualification.

## Service suite: dependency-qualified compatibility

For a second run, temporary directory junctions exposed the unchanged
source-side Chromium tree and historical SQLite fixture to the export. No
dependency payload was copied. The junctions and all generated `.docstream`
state were removed after the run, and the source prerequisites remained
present.

- 276 tests ran in 87.039 seconds.
- 276 passed; zero failed, errored, or skipped.
- The run included hardening, deterministic fuzzy-error, torture, persistence,
  rendering, MCP, native-vocabulary, relative-map, and theory-inspector tests.
- The native generated test retained 200 cases: 160 accepted batches and 40
  expected atomic rejections, with zero failures.
- The native torture test retained 501 streams across 500 transformations and
  5,010,000 reference slots.

This result proves compatibility with the specifically supplied prerequisites;
it does not place those prerequisites inside the repository or admit them as
automatic integrations.

## Research artifact suites

The reference-occurrence inspector Node suite ran 37 tests: 37 passed, zero
failed, zero skipped. It included rigid, fuzzy, and torture cases.

The reference-occurrence pilot Python suite ran 17 tests: 17 passed, zero
failed. It included rigid conformance, deterministic fuzzy-error, and bounded
torture cases.

## Cleanup verification

After testing:

- the temporary Chromium junction was absent;
- the temporary visual-example fixture junction was absent;
- the export `.docstream` runtime directory was absent;
- the source Chromium directory remained present;
- the source historical SQLite fixture remained present; and
- the export contained zero reparse points.

## Retained limitations

- Rendering tests require an admitted, project-local Chromium payload at
  runtime; that payload is not in this repository.
- The historical visual-example compatibility test requires an external SQLite
  fixture; that fixture is not in this repository.
- WordNet intake is documentation-only. No dictionary payload is present.
- External document conversion, GPU execution, and agentic control remain
  behind explicit integration barriers.
- Repository checks do not establish the legal status, authenticity, or
  continued availability of external resources.
