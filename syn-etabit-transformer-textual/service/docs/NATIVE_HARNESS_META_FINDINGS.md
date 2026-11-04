# Harness verification findings

Date: 2026-10-30. AUTH-14. Native profile: `docstream.native.safe-ascii/1`.

Two native-harness reporting defects were demonstrated before correction.
Their failures remain in
`../../.docstream/native-harness-meta-runs/auth14-20261030-before/`.
That run completed 28 hardening checks and 1,000 fuzzy cases: 11 hardening
failures and 80 fuzzy failures exposed the two defect groups below. These are
91 failing test cases, not 91 independent defects. The ten initial verification
methods also recorded 11 failing assertions/subtests. Original inputs, event
records, reports and a 15-file source snapshot remain available.

## NH-D02 — Unverified worker summary could become PASS

The supervisor accepted a worker's summary without reconciling it with the
journal and retained inputs. A controlled worker double produced a PASS while
the journal contained a failed case, or while saved evidence was incomplete or
contradictory. The double launches no child and never changes product files.

The fixed hardening cases exercise ten conditions:

- A journal failure contradicts a PASS summary.
- A started case has no completion event.
- A saved input has changed bytes or is missing.
- Summary counts or schema are wrong.
- Summary identity differs from the journal.
- An input path escapes the evidence directory.
- A summary duplicates a case identity.
- A malformed record appears in the middle of the journal.

The count is ten because changed and missing inputs are separate checks, as are
incorrect counts and schema. Forty fuzzy cases independently repeat the
failure-journal contradiction. The initial target incorrectly returned PASS;
the corrected target retains FAIL for observed failures and returns INCOMPLETE
for unverified evidence when no failure has been observed.

Correction: `native_harness/audit.py` reads the retained journal, validates saved
inputs against the planned cases, verifies their hashes and identities, checks
counts/completion/worker exit, and reports audit issues. The supervisor writes
`audited-summary.json` separately from the original worker `summary.json`.
Its final aggregation uses the audited result. Case schema `/1` stays compatible;
the reporting implementation is now `docstream.native-harness/1.1`.

## NH-D03 — Recovery could overwrite an observed failure

A journal with `case_failed: FAIL` followed by `case_finished: PASS` for the same
case caused recovery to overwrite the failure. The resulting status could be
INCOMPLETE instead of FAIL. A later event therefore erased failure evidence
from the recovered result even though the original journal retained it.

The fixed hardening case and 40 fuzzy cases demonstrate this. Corrected recovery
makes an observed failure sticky and records the contradictory event as an
audit issue. Twenty interrupted-journal torture recoveries also preserve FAIL.
Interrupted shrinking continues to retain the original failure before optional
reduction. The historical NH-D01 owned-descendant cleanup correction remains
in place and is exercised by the timeout checks.

## Corrected harness and native results

The fresh meta run `auth14-20261030-final` passes all 28 hardening checks,
1,000 fuzzy cases and eight torture scenarios. Its 16 deliberately stalled-child
termination cycles all confirm stopped children. The independent outer journal,
input hashes and source identity audit reports no mismatch. The 17 existing
native-harness and 11 new meta verification methods pass together.

The fresh native run `auth14-20261030-native` passes 100 hardening checks,
1,000 fuzzy cases and eight torture scenarios. All 1,108 saved input hashes
match; there are no native mode audit issues or unexpected native failures.
Thirty existing fixed native checks also pass. These results establish the
stated bounded properties; they do not establish that every possible corruption,
interleaving, operating-system failure or adversarial input is covered.

## Existing service findings remain separate

HF-01 concerns CR-to-LF DOCX conversion without a conversion-loss diagnostic.
HF-02 concerns NUL export producing an unclassified adapter failure/generic
service error. HF-03 concerns malformed-surrogate direct dictionary ingestion
raising UnicodeEncodeError before typed rejection. Their original descriptions,
replays and policy boundaries remain in HARNESS_FINDINGS.md.

AUTH-14 authorizes a fresh full service run and faithful reporting of those
outcomes. It does not authorize product repairs or a broader equivalence rule.
See NATIVE_HARNESS_META_VALIDATION.md for the current service counts and exact
run evidence. A passing native model cannot clear format or service findings.

## Preservation and limits

The initial 77-file snapshot has exactly two changed pre-existing files:
`native_harness/runner.py` and `native_harness/__init__.py`, both within the
approved harness correction scope. The other 75 protected files retain their
hashes, including product/native source, existing tests, metadata/locks and
snapshotted historical reports. The new audit module and meta package are
additions. No native/service product behavior, baseline, comparator or old
evidence file was rewritten.

Both failure groups concern evidence/reporting boundaries. No product defect
was inferred merely from a deliberately failing actor. Source hashes establish
byte identity, and local tests establish only their stated outcomes. Neither
is independent attestation or production acceptance. Agentic-control
integration remains last and outside this scope.
