# Instrumentation — deterministic Mill controller tooling

This package contains three small local controllers that move repetitive,
mechanical Mill Factory operation out of an LLM prompt and into inspectable
code.  They are published as a bounded research artifact inside the wider xOSG
instrumentation family.

Each controller is deliberately narrow.  It accepts one request, checks a
separate authority assertion, records what it observed, calls one unchanged
Mill interface, and retains a receipt.  It does not create authority, decide
whether evidence is true, promote a batch, repair a failed operation, or
coordinate arbitrary tools.

## Required entry point — read this before use

This document is the required entry point for this package. Before copying a
command, preparing a request or authority assertion, or invoking any controller,
you must:

1. read this entry point and [How to use the tooling](HOW_TO_USE.md);
2. read [Validation](VALIDATION.md) and
   [Provenance](PROVENANCE.md) so that test scope and source boundaries remain
   visible; and
3. read the README for the one controller you intend to use.

Do not infer permission from an example, a schema, a successful test, a
controller receipt, or this package's presence in the repository. The
controller checks a supplied authority assertion; it does not create the
human decision that makes a workload allowed.

## Tools

| Controller | Existing Mill interface | Narrow operation | Current public evidence boundary |
| --- | --- | --- | --- |
| [Creation](mill-controllers/creation/README.md) | `New-MillBatch.ps1` | Create one new HOLD batch at an authorized destination. | Basic validation and controller-specific hardening are retained; direct invocation can bypass its lease. |
| [Verification](mill-controllers/verification/README.md) | `Test-MillBatch.ps1` | Structurally validate one authorized batch. | Basic validation, controller-specific hardening, and a bounded controller/LLM comparison are retained. |
| [Gate recording](mill-controllers/gate/README.md) | `Set-MillGate.ps1` | Record one bound gate state with bound in-batch evidence when required. | Twelve basic integration cases and independent structural checks are retained; no hardening or LLM comparison is claimed. |

The controllers use the Python standard library and an existing PowerShell
launcher.  They require a compatible local checkout of the existing
[Mill Factory](../mill-factory/README.md); Mill Factory remains the tool that
performs batch creation, verification, or gate recording.

## Start here

1. Read [How to use the tooling](HOW_TO_USE.md) before invoking a controller.
2. Read [Validation](VALIDATION.md) to distinguish tested behavior from claims
   this package does not make.
3. Read [Provenance and publication boundary](PROVENANCE.md) for source
   identities, exclusion rules, and local-evidence limits.
4. Use one controller only within a separately authorized workload.  A request
   is not completion, and a structurally valid receipt is not semantic or
   promotion acceptance.

## Ongoing tool-by-tool example, not a generic wrapper

This package is an ongoing example of how a larger set of declared tools may
be examined and, where justified, given deterministic assistance. Its current
coverage is only three Mill interfaces: batch creation, structural verification,
and gate recording. It does **not** yet cover every Mill tool, every xOSG tool,
decision recording, promotion, recovery, scheduling, or a general orchestration
protocol.

Each possible next tool must be handled in its own sequence:

1. inspect its actual declared interface, inputs, writes, evidence, failure
   behavior, and source identity;
2. identify the specific repeated mechanical burden that should move out of an
   LLM prompt;
3. propose a controller that is fit for that particular tool and obtain scoped
   approval before implementation;
4. validate the controller against that tool's declared behavior; and
5. publish only evidence and claims supported by the resulting scope.

Tooling should be idiosyncratic when the tool is idiosyncratic. A creator,
validator, gate writer, importer, decision writer, or numerical worker can
share a few safety ideas without sharing the same request shape, authority
ceiling, state model, evidence condition, lease rule, recovery boundary, or
test suite. Do not flatten those differences into a generic wrapper merely to
make the package look uniform.

## Shared boundaries

- An authority JSON object is an asserted input.  The controller checks whether
  it binds to the request and declared source identity; it does not grant that
  authority.
- A SHA-256 digest establishes byte identity for the observed input or source.
  It does not establish truth, ownership, approval, compatibility, or meaning.
- A receipt separates admission, launched process, reported result, observed
  state, structural validation, retained state, and the next permitted action.
- `partial_or_unknown` is a retained result, not a reason to retry, delete,
  promote, or improvise recovery.
- These tools have no network service, automatic startup behavior, scheduler,
  agent registration, shared orchestrator, hypervisor, or bare-metal runtime.

The public source intentionally excludes local run directories, copied batches,
SQLite controller state, generated bytecode, raw process streams, and other
runtime evidence.  Those exclusions make this a reviewable tooling export, not
a full reconstruction of a local workspace.
