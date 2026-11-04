# xOSG-0 v0.4.0

**Expert Overlay System Gestalt — Bare-Metal 0**

![Version](https://img.shields.io/badge/version-0.4.0-blue)
![Stage](https://img.shields.io/badge/stage-prototype-orange)
![Validation](https://img.shields.io/badge/fuzzy%20suite-107%2F107%20pass-brightgreen)

xOSG-0 is a human-directed orchestration and workflow-control substrate for explicit state, task decomposition, verification, provenance, persistence, and bounded failure handling.

Version **0.4.0** is the loose/fuzzy-hardening release. Its central question is not only whether the normal workflow succeeds, but whether malformed, ambiguous, interrupted, or partially valid conditions fail in controlled and inspectable ways.

> **Prototype status:** this repository path is a staging location. Nothing in this README implies production deployment, privilege escalation, autonomous authority, or modification of an underlying model.

## Theoretical applications

xOSG-0 is intended first as a research substrate for studying how complex human-directed AI and software workflows can remain inspectable when authority, state, uncertainty, failure, and verification are distributed across multiple layers.

Potential theoretical applications include:

- **Layered authority models** — studying how policy, workflow, runtime, and human decision authority can coexist without collapsing into a single implicit controller.
- **Human-led machine orchestration** — exploring systems where models assist with decomposition, synthesis, and coordination while the human operator retains binding decision agency.
- **Compatibility of heterogeneous systems** — testing how components with different assumptions, interfaces, capabilities, or failure modes can interact without requiring them to become identical.
- **Bounded autonomy research** — examining how useful machine initiative can exist inside explicit state, transition, verification, and authority constraints.
- **Fail-closed AI workflows** — modeling systems that expose uncertainty, malformed state, and incomplete evidence instead of converting ambiguity into apparent success.
- **Provenance-aware computation** — studying how outputs can carry enough execution history, evidence, and state context to support later inspection and attestation.
- **Stateful reasoning environments** — exploring whether persistent registers, explicit transitions, and durable workflow state improve continuity over prompt-only orchestration.
- **Adversarial workflow testing** — using fuzzing, malformed persistence, contradictory state, timing anomalies, and near-valid inputs to probe the behavior of orchestration systems.
- **Synthetic expert overlays** — investigating layered expert instructions and machine descriptions that reinforce one another without claiming to alter the underlying model.
- **Deterministic offload** — identifying which validation, transition, policy, and persistence checks can be moved from probabilistic reasoning into deterministic mechanisms.
- **Multi-instance coordination** — modeling interactions among distinct AI instances or software machines while preserving local identity, authority boundaries, and provenance.
- **Control-plane separation** — exploring architectures where execution, verification, policy, and authorization are deliberately separated rather than fused into one process.
- **Inspectable failure semantics** — treating rejection, invalidity, corruption, and blocked states as first-class outcomes rather than exceptional edge cases.
- **Experimental governance kernels** — providing a sandbox for researching monotonic restrictions, production gates, explicit release authority, and other governance structures before any production implementation.
- **Machine-readable capability envelopes** — studying universal descriptions of what a program, model, or service can safely do before it is composed into a larger workflow.

These are research directions, not claims that v0.4.0 already implements a formal solution to each problem.

## Core workflow

```text
INTAKE
  ↓
DECOMPOSE
  ↓
ASSIGN
  ↓
EXECUTE
  ↓
RECONCILE
  ↓
VERIFY
  ↓
DELIVER
  ↓
LOG
```

Supporting states include `IDLE` and `BLOCKED`.

The fundamental execution invariant is:

```text
requested_action != completed_action
```

A request, parsed instruction, or accepted objective is not treated as completed execution. Completion requires valid state progression, evidence, and verification.

## Architecture

```text
┌──────────────────────────────────────────────┐
│ 6. Validation                               │
│    deterministic tests + loose/fuzzy tests  │
├──────────────────────────────────────────────┤
│ 5. Stateful Runtime                         │
│    state + registers + locking + recovery   │
├──────────────────────────────────────────────┤
│ 4. Natural-Language Compatibility Layer     │
│    novice/plain-language interaction        │
├──────────────────────────────────────────────┤
│ 3. Operating Prompt                         │
│    direct technical operating instructions  │
├──────────────────────────────────────────────┤
│ 2. Technical Instrumentation                │
│    invariants + transition rules + bounds   │
├──────────────────────────────────────────────┤
│ 1. Machine Description                      │
│    identity + capabilities + constraints    │
└──────────────────────────────────────────────┘
```

The layers reinforce one another. Higher layers make the system easier to use; lower layers retain the operative constraints.

## Persistent working registers

xOSG-0 maintains five primary registers:

- `NOTES` — observations, findings, context, and decisions.
- `TODO` — outstanding work.
- `ERROR-LOG` — failures, anomalies, and rejected operations.
- `AGENDA` — immediate operational priorities.
- `ROADMAP` — longer-term development and sequencing.

## Hardened persistence

The v0.4.0 runtime treats state and register updates as one logical transaction:

```text
prepare mutation
      ↓
transaction journal
      ↓
atomic state write
      ↓
atomic register write
      ↓
commit
      ↓
journal removal
```

A valid interrupted transaction can be recovered. Malformed or unverifiable persistence is rejected rather than silently trusted.

## Fail-closed behavior

The preferred failure rule is:

```text
uncertain state → reject or report
```

not:

```text
uncertain state → silently continue
```

The hardening model covers conditions including:

- corrupted or truncated JSON;
- malformed nested structures;
- invalid verification records;
- illegal state transitions;
- oversized inputs;
- lock contention and stale locks;
- transaction-journal corruption;
- protected-path symlinks;
- unusual Unicode and control characters.

## Loose / fuzzy validation

v0.4.0 deliberately tests inputs that are not clean or conventionally valid.

Coverage includes ambiguous natural language, null values, malformed JSON, truncation, unusual whitespace, Unicode, combining and bidirectional characters, shell-like and path-like strings, markup-like input, boundary-sized values, randomized operation sequences, transaction interruption, and locking anomalies.

The harness distinguishes:

```text
PASS
CONTROLLED_REJECTION
FAIL
CRASH
TIMEOUT
```

Rejecting malformed input may be correct. Crashing or hanging is not.

### v0.4.0 validation snapshot

```text
Loose/fuzzy cases:       107
Passed:                  107
Failures:                  0
Crashes:                   0
Timeouts:                  0

CLI smoke test:          PASS
Python compilation:      PASS
Journal recovery:        PASS
Lock-bound behavior:     PASS
Corrupt JSON handling:   PASS
Unicode/noise handling:  PASS
```

Earlier fuzzing exposed nullable-verification crashes and raw parser exceptions. Those failure classes were hardened and converted into regression cases.

## Installation

The prototype reference runtime targets Python.

```bash
git clone https://github.com/alia-june/prototype.git
cd prototype/syn-xOSG-0
```

When the runtime files are present, initialize and validate with:

```bash
python runtime/xosg.py init
python runtime/xosg.py status
python runtime/xosg.py validate
```

Run deterministic tests:

```bash
python -m unittest discover -s tests
```

Run loose/fuzzy validation:

```bash
python tests/fuzzy_harness.py
```

> The `syn-xOSG-0` directory is being staged incrementally. Commands become executable as the corresponding runtime and test files are populated.

## Planned repository map

```text
syn-xOSG-0/
├── README.md
├── CHANGELOG.md
├── machine/
├── architecture/
├── prompts/
├── runtime/
├── schemas/
├── state/
├── tests/
├── validation/
└── manifests/
```

As those components are staged, this README will link directly to the technical documentation, test harness, validation reports, and release artifacts.

## Design principles

```text
No implied execution.
No implied privilege.
No implied verification.
No silent corruption recovery.
No fabricated success.
No unbounded mutation.
```

xOSG-0 is designed to expose uncertainty and invalidity rather than conceal them.

## Version lineage

```text
v0.1.x  Declarative specification
   ↓
v0.2.0  Stateful runtime
   ↓
v0.3.x  Deterministic testing and hardening
   ↓
v0.4.0  Loose/fuzzy hardening and boundary validation
```

## Scope

xOSG-0 v0.4.0 is a development reference implementation. It is not a secure operating system, cryptographic trust framework, production capability-security kernel, or autonomous multi-agent authority.

Its purpose is narrower: provide a disciplined orchestration substrate with explicit state, bounded behavior, inspectable provenance, and controlled failure semantics.

## Development cycle

```text
define
  ↓
implement
  ↓
test
  ↓
break
  ↓
observe
  ↓
harden
  ↓
regress
  ↓
fuzz again
```

A discovered failure should become either a stronger invariant or a permanent regression test.

---

**xOSG-0 v0.4.0**  
**Expert Overlay System Gestalt — Bare-Metal 0**

Primary focus:

```text
bounded behavior
explicit failure
preserved provenance
controlled state
no fabricated success
```
