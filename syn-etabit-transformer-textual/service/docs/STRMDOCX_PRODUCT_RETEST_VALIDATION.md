# Strmdocx corrected-harness product-retest validation

Date: 2026-10-31. AUTH-19C-A. Overall result: **PASS; no product repair indicated**.

## Evidence roots

- Service: `.docstream/harness-runs/auth19c-20261031-before/`
- Native: `.docstream/native-harness-runs/auth19c-20261031-before/`

Both destinations were absent before execution. No matching harness worker was
present before either run.

## Service run

The service run uses seed 20261029, harness `docstream.harness/1.3` and product
`docstream-cpu 0.2.0.dev4`.

| Mode | Result | Cases | Render calls | Service calls |
| --- | --- | ---: | ---: | ---: |
| Rigid | PASS | 119 | 18 | 0 |
| Fuzzy | PASS | 500 | 0 | 0 |
| Torture | PASS | 5 | 6 | 1,907 |

The overall run passes in 173.157 seconds with 24 render calls. It reports
42,444,705 retained bytes before the final summary, below 512 MiB. The actual
post-report evidence tree is 42,812,939 bytes.

Each mode has complete coverage, a started owned worker, confirmed cleanup,
atomic job assignment before resume, job active count zero and an explicit
stopped result. The strict independent meta-auditor returns an empty issue list.
All 624 service cases are reconciled through that audit. `product_files_changed`
is empty.

Service evidence hashes:

- `run.json`: `14b478d2d391c2a341a88b5aa0d8eabf97e93f3fe5097e597396424fa87e2d78`
- `summary.json`: `210b8a35c7265fa98e1eb662ae11730499dff5ea906c0712f1a7744f7b5ca14c`
- `REPORT.md`: `752258b8980c2c50e91252552331a34ddbb75da2f2d79697a8cea513a34f5343`

## Native run

The native run uses seed 20261029 and harness
`docstream.native-harness/1.1`.

| Mode | Result | Cases | Submitted attempts | Supervisor seconds |
| --- | --- | ---: | ---: | ---: |
| Hardening | PASS | 100 | 54 | 0.531 |
| Fuzzy-error | PASS | 1,000 | 730 | 1.156 |
| Torture | PASS | 8 | 736 | 8.812 |

The run submits 1,520 transformation attempts. It reports 2,100,854 retained
bytes before final reports; the complete post-report tree is 2,494,838 bytes.
The highest observed Windows job committed-memory peak is 77,848,576 bytes.
This is an observation, not a leak or capacity certification.

All 1,108 native input files exist and match their recorded raw SHA-256. The
fuzzy distribution is exactly 800 error cases and 200 valid controls. All 800
expected rejections have the declared `NativeError`, a concrete error code and
an unchanged complete state fingerprint. Each mode's audited summary has zero
audit issues and zero interrupted cases. Product hashes before and after are
identical; `changed_product_files` is empty.

Native evidence hashes:

- `RUN.json`: `c31b308f7b420c143902b9c6ab8288a5ce45199c09e7b79eaba016a9171f97ca`
- `summary.json`: `a4c1289b01c25d86e20bfe4b84c1bc66e85203ed637ad8eb3e6de11c0fdfe031`
- `REPORT.md`: `4a62807e05bf0843d015995d53a60adb0c99e8097eec85a8f9723a7c266a1840`

## Independent final checks

Across both harnesses, 1,732 case inputs are retained and reconciled: 624
service and 1,108 native. Six process-output/native-mode logs permit exclusive
read opening with Windows sharing disabled. Final inventory finds zero matching
Python harness workers and zero project-launched Chromium/Edge workers.

No product or dependency file was changed. The result therefore closes
AUTH-19C-A as a passing product retest and does not open AUTH-19C-B repair work.

## Proof boundary

These are local bounded Windows observations. They do not prove independent
attestation, universal format fidelity, arbitrary-input safety, leak absence,
production scale, GPU equivalence, release readiness or live agent integration.
