# SSMI v0.2.1 validation results

These results are from the recorded v0.2.1 release run. They are not a new benchmark of this distribution.

- All five packaged regression scripts passed, and all 74 fixtures passed structural validation.
- The full fixture benchmark passed **48 of 74 cases (64.9%)**. The 26 failures remain in the [benchmark report](../engine/benchmark-report.md) and [detailed JSON results](../engine/benchmark-report.json).
- The distribution retains the 74 release fixture files byte-for-byte. Temporary paths in the benchmark JSON are represented as `candidate.json`.

| Coverage target | Distinct fixtures | Minimum | Status |
| --- | ---: | ---: | --- |
| `IMPLICATION.MACRO_DYNAMICS` | 8 | 6 | COVERED |
| `CONFLICTED` | 4 | 4 | COVERED |
| `NOT_APPLICABLE` | 4 | 4 | COVERED |

Fixture coverage measures representation, not interpretation accuracy. The grader detects explicitly forbidden claims and checks structured source and dependency records. These checks do not establish that every additional claim is supported. The prototype operates on synthetic text and supplied textual descriptions; no real-world perception or independent attestation is claimed.
