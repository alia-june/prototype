# Validation boundary

This document summarizes retained local validation evidence for the public
controller sources.  It does not publish raw local runtime directories,
controller SQLite state, copied batch contents, or full process streams.

## Ongoing coverage is deliberately incomplete

The three published controllers are an ongoing, tool-by-tool example—not a
claim that every Mill or xOSG tool has been instrumented. The current evidence
does not admit an uninspected tool into this package. Each later tool needs its
own source inspection, explicit workload and development scope, fit-for-purpose
controller design, validation, and evidence boundary.

The design is intentionally idiosyncratic where tools differ. Shared ideas such
as authority binding, source identity, receipts, and visible uncertainty do not
justify a single generic request schema, writer policy, recovery action, or
test suite for tools with different state transitions and evidence conditions.

## Evidence summary

| Controller | Retained local validation | What the result establishes | What remains outside the result |
| --- | --- | --- | --- |
| Creation | Six basic controller checks and one controller-mediated Mill creation; later twelve deterministic checks, 1,000 seeded admission-only fuzz cases, and twenty 32-way contention rounds. | The declared controller behavior on the inspected host/source identity, including its retained lease and receipt behavior. | Universal safety, direct-invocation protection, semantic acceptance, generic orchestration, compilation, or whole-system LLM savings. |
| Verification | Eight basic checks; later fourteen deterministic checks, 1,000 no-launch fuzz cases, and twenty rounds of 32-way same-target contention.  A separate 20-case comparison recorded zero controller LLM calls. | The declared validation-controller behavior and the measured bounded comparison results. | Whole-system/lifetime savings, generic protocol safety, source semantics, or unrelated workloads. |
| Gate recording | Twelve basic integration cases passed after preserving an earlier fixture-layout failure; five resulting copied batches separately passed the unchanged Mill structural validator. | The declared gate-controller behavior for its basic cases, including evidence digest binding and receipt separation. | Fuzzing, torture, concurrency hardening, LLM comparison, promotion, decision writing, or a no-LLM network-egress proof. |

## Important interpretation rules

- A source tool reporting `BATCH_CREATED` or `GATE_RECORDED` is not by itself
  proof that every intended artifact is valid.
- A Mill structural `PASS` establishes only the factory's declared structural
  and internal-consistency checks for that batch.  It does not prove that a
  claim, gate evidence, runtime result, or promotion is correct.
- The creation and verification controller records that make zero LLM operating
  calls do not prove that no AI was involved in a person's earlier planning,
  that the host made no unrelated network connection, or that a later tool
  revision has the same behavior.
- The gate controller is intentionally reported more narrowly: it has basic
  validation only.  It has not received the creation/verification hardening or
  comparison treatment.
- Earlier failed or corrected runs remain part of local evidence.  A later
  successful retry does not erase the earlier failure; it identifies the
  corrected condition and its separate result.

## Reproducing a bounded check

Use the included unit tests and harnesses only with an authorized local test
root and a compatible Mill Factory checkout.  The harnesses create task data
and controller state; do not run them inside the Mill source tree or against an
unapproved production batch.  In this repository, public test defaults resolve
to the sibling `mill-factory/` directory.  Set `MILL_FACTORY_ROOT` to point at
another compatible checkout when that is the intended test subject.

Before interpreting a rerun, compare the local Mill script hashes to the
identities in [Provenance](PROVENANCE.md), retain the generated receipts, and
record any changed interpreter, operating system, source, or test fixture.
