# ES-xOSG-0 — expert-system-enabled xOSG-0 working example

This is a small, non-executing expert-system example under
[Instrumentation](../README.md). It demonstrates one next layer above
tool-specific controllers: consume explicit retained receipt facts, apply
deterministic rules, and return a bounded human-facing state.

It is not a historical xOSG-0 stage, recovered ES-xOSG-7 source, a replacement
for the canonical xOSG-0 growth spine, a Seed extraction, a generic orchestral
runtime, or a claim that every tool can share one schema.

## What it does

The example accepts one explicit receipt envelope for one of three currently
mapped tool kinds:

| Tool kind | Adapter source shape | Known-valid result |
| --- | --- | --- |
| `mill.creation` | Creation controller fields: `creation_reported`, `artifact_verification`, and retained state | `AWAIT_HUMAN_REVIEW` |
| `mill.verification` | Verification controller fields: nested `validator.reported_result`, process state, and retained state | `AWAIT_HUMAN_REVIEW` |
| `mill.gate` | Gate controller fields: `gate_write_reported`, `structural_validation`, and retained state | `AWAIT_HUMAN_REVIEW` |

Every result is one of:

```text
AWAIT_HUMAN_REVIEW
STOP_AND_RETAIN
NEEDS_AUTHORITY
UNMAPPED_OR_INSUFFICIENT_RECEIPT
```

The example never upgrades a receipt into acceptance, truth, promotion, or
execution authority.

## Run a fixture

```text
python expert_system.py fixtures/gate-known-valid.json
```

The program reads one JSON envelope and prints one decision JSON object. It
uses the Python standard library only. It has no subprocess, network, LLM,
controller-invocation, Mill-write, retry, scheduling, or recovery capability.

## Why the adapters are idiosyncratic

The rule core is small, but its inputs are not flattened. The three controllers
emit different evidence shapes because the underlying tools do different work.
The adapters translate only the named fields documented in this example. An
unknown tool kind, missing field, or unrecognized state is refused rather than
coerced into a generic success result.

See [Validation](VALIDATION.md) and [Provenance](PROVENANCE.md) before treating
this example as evidence beyond its stated fixture behavior.
