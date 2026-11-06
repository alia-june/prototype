# How to use the deterministic Mill controller tooling

## What this guide is for

Use this guide when a human has already decided that a particular Mill Factory
operation is allowed and wants a controller to perform the repeatable mechanics
without asking an LLM to reconstruct paths, input rules, source identities,
leases, process output, or receipt state.

This guide is not approval to create a batch, record a gate, or treat a result
as accepted.  The workload owner remains responsible for the intended outcome,
scope, authority assertion, evidence, and any decision after a receipt.

## Choose one operation

| Need | Controller | Existing Mill action |
| --- | --- | --- |
| Create a new non-overwriting HOLD batch | `mill-controllers/creation/` | `New-MillBatch.ps1` |
| Check one existing batch for Mill structure and manifest consistency | `mill-controllers/verification/` | `Test-MillBatch.ps1` |
| Record one pending/pass/fail/blocked gate state | `mill-controllers/gate/` | `Set-MillGate.ps1` |

Do not combine these into a general workflow.  Complete, review, and retain
the receipt for one operation before beginning another authorized operation.

## Before invoking a controller

1. Identify the exact Mill Factory checkout.  It must contain the declared
   PowerShell interface and any helper scripts the controller identifies.
2. Create a new, task-owned controller state directory outside the Mill source
   tree.  Controller state can contain leases and receipts; it is not source.
3. Prepare one request JSON file using the controller's example schema where
   supplied.
4. Prepare a separate authority JSON file.  Bind it to the canonical request
   digest, the controller-observed Mill source identity, and the allowed batch
   or output root.  For evidence-bearing gate results, bind the SHA-256 of the
   already-existing evidence file.
5. Confirm that the intended destination is safe to use and that the authority
   names the required root.  Do not rely on a controller default to decide a
   vague or missing human choice.

## Invoke exactly one operation

All three controllers use this command shape:

```text
python controller.py --tool-root <mill-factory-path> --state-root <new-task-state> request.json authority.json
```

Run the command from the selected controller directory.  The controller must
use an already-installed Python interpreter and PowerShell launcher.  Do not
install a dependency, alter the Mill source, patch a controller, or substitute
a helper merely to make one workload proceed.

The individual READMEs describe their additional request fields:

- [Creation request and authority examples](mill-controllers/creation/README.md)
- [Verification request and authority examples](mill-controllers/verification/README.md)
- [Gate evidence and result requirements](mill-controllers/gate/README.md)

## Read the receipt instead of guessing

The exact receipt fields differ by controller, but interpret them separately:

| Receipt fact | Meaning | It does not mean |
| --- | --- | --- |
| `admission` | The bound request passed the controller's known preconditions. | The requested action is substantively good or fully authorized beyond the assertion. |
| `process_outcome` | What process launch, exit, timeout, and captured output were observed. | The source tool completed every intended effect. |
| reported result | The source tool reported its declared success object. | Artifacts, manifests, or evidence are correct. |
| structural validation | The declared Mill structural checker returned its result. | Semantic correctness, runtime behavior, acceptance, or promotion. |
| `retained_state` | Whether the controller retained a known receipt or an uncertain outcome. | Permission to retry, delete, repair, or promote. |
| `next_permitted_action` | The controller's constrained continuation label. | A replacement for a human decision. |

If the result is `partial_or_unknown`, stop the operation.  Preserve the
receipt and the batch state.  A recovery action requires fresh scope and
authority; do not automatically rerun the tool.

## Keep the LLM outside the operation

An LLM may help a person express a goal or draft a request for review, but it
need not operate these controllers.  The controller, not an LLM prompt,
performs the declared mechanical preflight, lease handling, invocation,
observation, and receipt retention.

That is a scope boundary, not a claim that an LLM never exists elsewhere on the
host, that an authority assertion is true, or that controller construction and
maintenance cost nothing.  See [Validation](VALIDATION.md) for the exact
evidence available for each controller.
