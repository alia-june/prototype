# Test Evidence and Proof Limits

## Current execution environment

- Date: 2026-10-31.
- Execution: local Python available in the current Codex environment.
- Dependencies installed: none.
- Network invoked: no.
- Sources executed from: isolated system temporary extraction.
- Original archives modified: no.
- Strmdocx runtime or service imported: no.

## Manifest and JSON results

| Check | Covered | Failures |
| --- | ---: | ---: |
| Holon handoff manifest | 15 | 0 |
| UPST v0.1 manifest | 13 | 0 |
| UPTI v0.2 manifest | 33 | 0 |
| Nested UPTI-SF manifest | 9 | 0 |
| Strict JSON parse with duplicate-key/nonstandard-constant rejection | 30 files | 0 |

## v0.1 test rerun

Command:

```text
python -m unittest discover -s tests -p test_*.py -v
```

Observed result: **10 tests run, 10 passed, exit code 0.**

Covered themes include golden vectors, exact zero versus absence, KLEENE UNKNOWN, opaque grades, balanced-domain masks, failure versus propagated marker, unresolved radix-nine semantics, malformed/unsupported data, JSON hardening and inert artifact references.

## v0.2 test rerun

Command:

```text
python -m unittest discover -s tests -p test_*.py -v
```

Observed result: **34 tests run, 34 passed, exit code 0.**

This includes the unchanged 10 v0.1 tests plus local staging, state-transition, exact-byte, mutation, duplicate-ID, profile, capacity, hostile depth/width, invalid-surrogate, receipt and local replay tests.

## Historical test claims not rerun

The nested UPTI-SF report claims earlier:

- 25/25 integration tests;
- fuzzy testing;
- torture testing;
- crash-oriented testing.

The nested package contains no historical runtime or complete test corpus. Those claims remain `VALIDATION_CLAIM`, not current `VALIDATION_RESULT`.

## Preserved assistant errors

1. Initial v0.2 extension parsing accepted a 1,300-level nested array. The corrected code adds iterative depth and node limits.
2. Initial invalid-Unicode test used literal escape text instead of a surrogate code point. The corrected fixture constructs and rejects an actual unpaired surrogate.

The current suite passes the corrected cases. That does not erase the original errors or prove general memory safety.

## What the passing tests establish

- The supplied validator and local staging code exhibit the tested behavior in this environment.
- The tested examples and negative inputs are handled as asserted by the current test suites.
- The exact-byte local round trip passes for the supplied test construction.
- Explicit negative remote receipt fields remain false.

## What they do not establish

- Accepted UPTI or UPST conformance.
- A network transfer or receiver call.
- Authenticated sender or receiver identity.
- Authorization, permission or user approval.
- Encryption, signature or keyed integrity.
- Durable replay/freshness protection.
- Security against same-process hostile code.
- Artifact existence or transfer.
- Complete fuzz/torture/crash coverage.
- General semantic equivalence.
- Correctness of the absent Holoquary v1.2 baseline.
- Strmdocx integration or runtime behavior.
- Independent attestation.

## Evidence rule

Use `VALIDATION_RESULT` only for checks observed in this run. Use `VALIDATION_CLAIM` for source-reported checks not reproduced. A hash, schema pass, local unit pass, fallback or recovery must retain its exact proof class and must not be laundered into a stronger result.
