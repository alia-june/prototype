# Reference-Occurrence Pilot Validation

Date: 2026-11-01  
Result: **PASS for the bounded pilot contract and stated tests.**

## Approved scope

The user cleared the production gate with **“yes”** after receiving the exact occurrence/reference-holon proposal. The approval covers this fixture-specific research package, its strict validator, and its rigid, deterministic fuzzy, and bounded torture tests. The clearance and its exclusions are recorded in `REFERENCE_OCCURRENCE_DECISION.md`.

## Environment and dependencies

- Execution platform: the current local Windows workspace.
- Runtime: the available `python` command.
- Dependencies installed: none.
- Libraries used: Python standard library only.
- Network, database, service, GPU, and receiver activity: none.
- Existing Strmdocx product files modified: none outside this new research directory.

## Final executed checks

The following final commands completed with exit code 0 from this directory:

```text
python -m py_compile validate_reference_occurrence.py test_reference_occurrence.py
python validate_reference_occurrence.py
python -m unittest -v test_reference_occurrence.py
```

Observed validator result:

```text
PASS: reference-occurrence fixture satisfies the bounded pilot contract
```

Observed final unit-test result:

```text
Ran 17 tests in 0.226s
OK
```

Elapsed time is an observation from one run, not a performance guarantee.

## Rigid lane

Seven rigid test methods passed. They checked:

1. the exact fixture has zero findings;
2. V0 and V1 contain the same occurrence set in the two required orders;
3. occurrence records contain only their identity/kind and three scalar references;
4. all three target payload digests reproduce under the declared canonicalization;
5. repeated validation is deterministic;
6. duplicate JSON properties are rejected; and
7. nonstandard numeric constants, malformed/trailing JSON, invalid UTF-8, and an over-limit input byte stream are rejected.

The independently executed command-line validator also loaded the machine contract through its strict loader and validated the exact fixture.

## Deterministic fuzzy-error lane

Two fuzzy test methods passed.

One method applied twenty named semantic mutations independently and checked that every mutation was rejected with the same ordered findings on two executions:

- missing target;
- wrong target-reference family;
- malformed identifier;
- duplicate identifier;
- unknown root field;
- unknown occurrence field;
- missing relationship reference;
- missing metadata reference;
- embedded target object;
- altered chronological order;
- inconsistent view occurrence set;
- payload-digest tamper;
- native JSON null;
- over-limit string;
- transformation input mismatch;
- relationship/result mismatch;
- embedded reference array;
- wrong record kind;
- duplicate occurrence reference within one view; and
- malformed digest.

The other method rejected four malformed byte-stream classes: truncated JSON, duplicate properties, `Infinity`, and invalid UTF-8. It also rejected a byte stream larger than an explicitly supplied loader limit.

These are deterministic fault cases, not random coverage or exhaustive fuzzing.

## Bounded torture lane

Eight torture test methods passed:

| Case | Bound exercised | Observed result |
| --- | ---: | --- |
| Repeat accepted validation | 1,000 complete validations | All returned zero findings. |
| Large inspection orders | 2,048 distinct occurrence holons, forward and reverse views | Accepted structurally. |
| Permuted views | 128 occurrences across 64 deterministic permutations | Accepted twice with identical results. |
| Transformation chain | 128 append transformations, 257 targets, 128 relationships, 384 occurrences | Accepted structurally in forward and reverse inspection. |
| Unresolved-reference storm | 512 unresolved target references | Rejected; findings capped at the contract maximum of 128. |
| Deep embedded reference | 1,000 nested objects in a reference field | Rejected without recursive validator failure. |
| Non-JSON direct-call payload | Set value supplied directly to the Python API | Rejected; canonicalization failure became a finding rather than a crash. |
| Rejection isolation | 500 independently rejected candidates | Accepted fixture bytes remained unchanged and passed afterward. |

“Accepted structurally” means the generated document satisfied the shared record/reference rules with the exact fixture profile intentionally disabled. It does not adopt those generated sizes, chains, or permutations as real-document policy.

## Harness hardening history

An initial 16-test run passed. A subsequent hardening test was added to exercise canonical-serialization failure. Two intermediate executions each had one failed **test assertion** because the test assumed Python’s JSON serializer would fail at 1,000 and then 5,000 levels of acyclic mapping; on this runtime it did not. The validator still rejected those documents for schema reasons and did not crash. The test was corrected to use a deterministic non-JSON direct-call value, which exercises the intended exception-to-finding branch. The final 17-test run passed.

This history is retained to distinguish a harness-assumption correction from a product or reference-model defect.

## Output hygiene and manifest validation

Python created a local `__pycache__` directory during compilation. The first exact-path recursive cleanup command was blocked before execution by command policy. A second PowerShell operation used validated absolute paths and the platform directory API; it removed only the pilot’s generated cache and verified that the directory no longer existed.

`SOURCE_MANIFEST.json` excludes itself. After the other eight approved artifacts were finalized, their byte sizes and SHA-256 values were recorded. A separate read-back check then verifies:

- the manifest parses with duplicate-property rejection;
- every listed path is a direct file in this package;
- every listed size and SHA-256 matches the final bytes;
- the eight expected nonmanifest artifacts are covered exactly; and
- no unexpected nonmanifest file is present.

## What this proves

Within the executed environment, the evidence supports these bounded conclusions:

- the fixture has separately addressed target, relationship, metadata, occurrence, and view records;
- occurrence and view records use references rather than embedded target bodies;
- chronological and reverse inspection reuse the same occurrence identities without mutating history;
- the fixture transformation maps `abc` plus `!` to `abc!` and its target payloads have reproducible digests;
- the validator fails closed for the enumerated malformed inputs; and
- the harness remains deterministic and state-isolated under the stated stress bounds.

## What this does not prove

This validation does not establish:

- that the occurrence/reference-holon form is the final or universal native schema;
- authenticity, authorship, authority, trusted time, or independent attestation;
- correct semantics for arbitrary transformations;
- safe transformation cancellation, reversal, commutation, deduplication, or bypass;
- arbitrary graph recursion, cycle handling, ownership, deletion, lifetime, or garbage collection;
- rendering or reconstruction fidelity for Markdown, HTML, Python, DOCX, GPU, or other profiles;
- transport, delivery, authentication, authorization, encryption, or receipt behavior;
- database durability, concurrency, crash recovery, or service integration;
- security certification, exhaustive fuzzing, or denial-of-service resistance; or
- correctness of the wider Strmdocx runtime.

SHA-256 here establishes byte identity only for the named payload canonicalizations and final package files. It does not elevate this pilot to canon or production-service acceptance.
