# Reference-Occurrence Inspector Validation

Date: 2026-11-01  
Result: **PASS for the approved bounded offline inspector, subject to the stated direct-file automation limit.**

## Production clearance

The user approved the exact nine-file inspector proposal with **“yes”** on 2026-11-01. The clearance covered this new sibling directory, a provenance-bearing display snapshot of the completed pilot, the read-only interface, a JavaScript rigid/fuzzy/torture harness, local browser QA and final integrity evidence.

The clearance did not authorize editing, transformation execution, rollback, cancellation, bypass, a database, a service, network integration, GPU work, WordNet/Etabit integration, agentic control, changes to the completed pilot or changes to the existing Docstream runtime.

## Implementation boundary

The inspector is a buildless HTML/CSS/JavaScript application. It has:

- no installed dependencies;
- no framework or build step;
- no hosting identity or deployment configuration;
- no external script, style, font, image or data request;
- no fetch call;
- no editing, persistence or effect controls; and
- no dynamic HTML insertion of source-derived values.

The Sites skill was used for its local-only implementation and preview discipline. Its hosted registration, source synchronization, packaging, saving and publication steps were intentionally skipped because the approved scope is local-only.

## Governing source identity

The resolved display packet records and the test harness independently rechecked these untouched sibling files:

| Role | Source | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Machine contract | `../reference-occurrence-pilot-20261101/reference_occurrence_contract.json` | 3,838 | `a5a22653b719a9057dbc226751a946fdffb6beb463392ad0f7c9b8a02a126bda` |
| Pilot fixture | `../reference-occurrence-pilot-20261101/reference_occurrence_fixture.json` | 2,569 | `b605410ead9f1bf40c58b66c397269e9e4ffa6289ca1697b8f4c6f8cc890c7a5` |

The existing strict Python validator was executed against those exact source files after the inspector implementation:

```text
PASS: reference-occurrence fixture satisfies the bounded pilot contract
```

`data.js` is explicitly labeled a `read_only_resolved_display_packet`. It permits reliable offline presentation without making the display copy native storage or a new authority source.

## Automated JavaScript checks

The following commands completed with exit code 0:

```text
node --check data.js
node --check inspector-core.js
node --check app.js
node --test test_inspector.mjs
```

Final observed result:

```text
tests 37
pass 37
fail 0
cancelled 0
skipped 0
todo 0
duration_ms 454.2978
```

Elapsed time is an observation from one final run, not a performance guarantee.

### Rigid lane

Eight top-level rigid checks passed:

1. the two display-packet source identities match the current sibling bytes and SHA-256 values;
2. the accepted snapshot has zero findings and all three target digests are verified;
3. record counts are exactly three targets, one relationship, one metadata record, three occurrences and two views;
4. V0 is O0/O1/O2 and V1 is O2/O1/O0;
5. view comparison reports the same occurrence set, different order, no history mutation and no rollback;
6. every occurrence resolves its target, relationship and metadata references;
7. canonical browser-side SHA-256 reproduces all three target payload digests; and
8. the renderer contains no `innerHTML`, `insertAdjacentHTML`, `document.write`, `eval` or `new Function` sink and uses `textContent` for source-derived display.

### Deterministic fuzzy-error lane

Twenty named semantic mutations were independently rejected. Each candidate was analyzed twice and produced the same ordered findings:

- missing target;
- wrong target family;
- malformed identifier;
- duplicate identifier;
- unknown fixture-root field;
- unknown occurrence field;
- missing relationship reference;
- missing metadata reference;
- embedded target body;
- altered chronological order;
- inconsistent view occurrence set;
- digest tampering;
- native JSON null;
- over-limit string;
- transformation input mismatch;
- relationship/result mismatch;
- embedded reference array;
- wrong kind;
- duplicate occurrence within one view; and
- malformed digest.

A separate hostile-markup test placed image/event-handler and script-like text in the metadata provenance field. The model remained structurally valid because the value was ordinary text, and the renderer's text-only path retained it as inert text rather than interpreting it as markup.

### Bounded torture lane

Seven top-level torture checks passed:

| Case | Bound | Observed result |
| --- | ---: | --- |
| Repeated accepted analysis | 1,000 complete analyses | All valid |
| Large views | 2,048 distinct occurrences, forward and reverse | Valid; same set, different order |
| View permutations | 128 occurrences across 64 deterministic views | Valid twice with identical findings |
| Transformation chain | 128 transformations, 257 targets, 128 relationships and 384 occurrences | Valid structurally forward and backward |
| Broken-reference storm | 512 unresolved targets | Invalid; findings capped at 128 |
| Deep embedded reference | 1,000 nested objects in a reference field | Rejected without recursive failure |
| Rejection isolation | 500 rejected candidates | Source packet unchanged and valid afterward |

The generated torture packets were analyzed with the exact B0/T1/B1 profile disabled while the common record, reference, transformation, digest and resource rules remained active. Their acceptance does not adopt those generated sizes or structures as real-document policy.

## Local preview and browser QA

The installed local-preview guidance was read before previewing. A temporary owned Node HTTP server served only this package on loopback. The representative page returned:

```text
HTTP 200
Content-Type: text/html; charset=utf-8
```

The inspector was then inspected in the in-app browser. The live page visibly established:

- title and source-boundary labeling;
- snapshot status **verified**;
- three verified payload digests;
- record totals 3/1/1/3/2 and zero findings;
- V0 order O0 → O1 → O2;
- V1 order O2 → O1 → O0;
- reverse explanation that traversal changes but history does not;
- comparison result: occurrence set identical, order different, history mutation none;
- transformation selection and its canonical digest;
- reference following from T1 to B0;
- exact source paths, sizes and hashes in the source-identity dialog;
- a readable narrow-window layout; and
- a validation panel reporting no findings.

The browser console contained zero warnings and zero errors.

One initial accessibility-role locator did not match the T1 record-index toggle because `aria-pressed` exposed it as a checkbox-like toggle in this browser. No page state changed. The QA action was retargeted using the record's explicit `data-record-id`; selection, detail display, digest status and reference following then worked. This was an automation-selector mismatch, not an inspector defect.

### Direct-file automation limit

The approved application was designed for direct `file:///` opening: all resources are relative static files, scripts are classic scripts rather than modules, the snapshot is already local, and there are no fetch or network calls.

After HTTP preview QA, an automated attempt to navigate the test browser to the final local `file:///.../index.html` path was blocked before navigation by the browser-control URL policy, which permits only HTTP and HTTPS. No bypass or alternate browser workaround was attempted. Therefore:

- local HTTP behavior was directly observed and passed;
- source inspection supports file compatibility;
- actual direct-file opening was not independently executed by browser automation; and
- the user can open `index.html` directly in a normal local browser.

This is an automation proof limit, not evidence that the page requires a server.

## Final package integrity

After all eight nonmanifest files were finalized, `INSPECTOR_MANIFEST.json` was generated as a self-excluding manifest. A separate read-back check verifies:

- strict duplicate-rejecting JSON parsing of the manifest;
- exact coverage of the eight approved nonmanifest files;
- every recorded output byte size and SHA-256 value;
- both governing source byte sizes and SHA-256 values;
- accepted JavaScript model analysis with zero findings and three verified digests;
- no unexpected package file or directory;
- no cache or temporary artifact; and
- no unresolved work-marker token.

The temporary local preview server is stopped during final teardown and is not a product dependency or package artifact.

## What this proves

Within the stated environment and bounds, the evidence supports that:

- the inspector accurately presents the completed pilot snapshot;
- V0 and V1 reuse the same occurrence identities in different orders;
- reverse inspection does not alter the declared relationship or history;
- target, relationship and metadata references can be followed separately;
- the three target payloads match their recorded canonical SHA-256 values;
- the enumerated invalid models fail deterministically;
- rejected models do not mutate the accepted snapshot;
- source-derived values follow a text-only rendering path;
- the local preview is responsive and free of observed browser warnings/errors; and
- the source pilot remained byte-identical throughout the work.

## What this does not prove

This validation does not establish:

- that the occurrence-holon form is the final universal native schema;
- transformation execution, inverse execution, cancellation, commutation, equivalence or bypass;
- correctness for arbitrary operations or arbitrary recursive graphs;
- ownership, lifetime, deletion, revision, cycles or garbage collection;
- exhaustive browser compatibility or direct-file behavior in every browser;
- security certification or denial-of-service resistance;
- rendering fidelity for Markdown, HTML, Python, DOCX, GPU or another profile;
- database, service, transport, network, concurrency, crash-recovery or durability behavior;
- authenticity, authorship, authority, permission, trusted time or independent attestation;
- WordNet/Etabit integration; or
- agentic execution or control.

The inspector is a bounded read-only presentation and test instrument. It is not the Docstream runtime and does not elevate the pilot to general canon.
