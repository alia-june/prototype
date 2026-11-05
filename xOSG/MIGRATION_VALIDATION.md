# xOSG migration validation

Date: 2026-11-05

## Source and publication checks

- Pinned OpenSurface source revision: `276957db0f374edf6fc02b6919e2ec42c8960290`.
- All 136 baseline source files matched their Git blob identities before selection.
- All 100 xOSG files are accounted for: 95 byte-preserved; five documentation/checksum edits. Executable source and the complete sanitized failed-source subtree are unchanged.
- Every imported file received a complete-file UTF-8 residue scan for private home paths, personal addresses and known account markers, credential forms, private-key headers, and excluded artifacts. Publication documents, configuration, receipts, and broad keyword hits received contextual review. No actionable private residue was detected. Detection has limits and does not prove the absence of every possible secret.
- Source MIT grant and copyright notice are retained in LICENSE; existing inline and third-party notices remain. No whole-repository REUSE claim is made.
- Relative file links in the migrated documentation and updated project index are checked against the combined destination tree. The DWSK 36-entry source inventory and the failed-source manifest are verified.

## Fresh fixed DWSK checks

| Mode | Units | Self-checks | Total |
|---|---:|---:|---:|
| Ordinary Python | 17/17 | 7/7 | 24/24 |
| Optimized Python | 17/17 | 7/7 | 24/24 |
| Combined | 34/34 | 14/14 | 48/48 |

The fixed runner verified actual mode, named test sets, exact counts, absence of skipped tests, and owned process/job/stream/handle cleanup. Combined elapsed execution was 14.063 seconds within the approved 300-second cap. An initial orchestration timeout request was refused before worker launch because it exceeded the unchanged helper's 120-second per-worker limit; the local invocation was corrected and the refusal is retained privately. Product source was not changed.

These are overlapping development checks. They do not reproduce the 244-check R4 campaign, older fuzzy/installed/native-mutex campaigns, every OS/interpreter, physical power loss, logger integration, or a new binary release. Raw diagnostics and owned-execution receipts remain private.

## Retained failure and relocation limits

The defunct experiment remains failed. Its original Windows intake result is 42/43 and its sanitized-source report is 35/36; neither campaign is rerun here. Its archived visibility and license-status statements retain their historical context. See [MIGRATION.md](MIGRATION.md) for the later MIT grant and explicit public-relocation decision.

The source cleanup candidate retains all 36 non-xOSG files, with six navigation/licensing/provenance/validation/validator edits. Its repository validator passes 17/17. Camera Obscura shader identities and the 11-entry shader inventory are unchanged. This structural check does not requalify live shader behavior.

Public remote readback and the later OpenSurface cleanup are recorded in the separate local closure record after publication. A passing local check alone is not evidence that either remote operation has completed.
