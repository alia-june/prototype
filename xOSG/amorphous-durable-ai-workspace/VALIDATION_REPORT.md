# R4 source-adoption validation — 2026-11-04

Status: PASS for the stated source qualification in this review revision. Both actual ordinary and optimized Python modes were exercised on Windows. The adopted runtime/checker and development helper bytes match the qualified executable source identities; raw fixtures and private diagnostics remain outside this repository.

| Named set | Ordinary | Optimized |
|---|---:|---:|
| Recovery lifecycle | 24/24 | 24/24 |
| Value admission | 32/32 | 32/32 |
| Worker lifecycle | 16/16 | 16/16 |
| Checker controls | 26/26 | 26/26 |
| Existing units | 17/17 | 17/17 |
| Existing self-checks | 7/7 | 7/7 |
| R4 total | 122/122 | 122/122 |
| Added development runner, overlapping existing suites | 24/24 | 24/24 |

The 244 R4 checks and 48 entrypoint checks are separate invocations with overlapping coverage. Acceptance requires exact named sets, typed counts, actual mode, causal refusal controls and owned process/job/stream/handle cleanup. The fixed runner supports source-tree use and is not an installed runtime service.

Recovery failures retain output and an explicit guard for operator review. A verified workspace whose final acknowledgement/guard restoration fails is reported as verified-unacknowledged; that case is not claimed to remain guarded. Markers govern DWSK calls and are not OS permission interlocks. Native/database faults are controlled injections. Process interruption is not physical power-loss proof.

This adoption does not rerun the historical 1,000-case fuzzy campaign or installed-wheel campaign. It does not qualify every OS/interpreter, hostile namespace races, external SQLite tools, a logger, source authenticity, automatic notes/decisions or agent authority. The source checksum inventory is regenerated from the current curated bytes, excluding itself. No replacement wheel/sdist, version or release tag is claimed.

## Historical baseline source/build record

The following record describes its original 2026-10-31 source and binaries, before this adoption. Its historical outcomes do not identify or validate the changed source below.

# DWSK 0.1.1 source-validation basis — 2026-10-31

The runtime implementation is copied byte-for-byte from the validated mutex candidate. Version metadata changes to 0.1.1; packaging introduces no runtime behavior change.

The retained source campaign passed 32 hardening, 1,000 deterministic fuzzy and eight torture cases. Existing 17-unit, seven-self-validation and fifteen-CLI checks passed in both modes. Eight retry tests and twelve mutex tests passed in each mode. Twenty native four-process checkpoint trials (240 calls) completed without a surfaced worker failure. Native mutex tests exercised exclusion, timeout, real abandoned ownership and inconsistent-state refusal. Earlier failures remain retained historical evidence.

These are bounded Windows/Python 3.14 observations. They do not establish an OS root cause, exhaustive coverage, acceptance on every interpreter/OS, physical power-loss durability or application integration. The module boundary and durability contract remain applicable.

The rebuilt wheel must also pass outside-source installation checks. The accompanying BUILD_REPORT.md and artifact inventory record those results and artifact hashes. Source success alone does not prove the contents or imports of an installed wheel.

The original supplied report is preserved as docs/HISTORICAL_VALIDATION_0.1.0.md.
