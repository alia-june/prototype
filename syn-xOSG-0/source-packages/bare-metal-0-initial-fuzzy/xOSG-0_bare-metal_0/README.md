# xOSG-0
## Expert Overlay System Gestalt — Version Bare-Metal 0

**Actualized workspace artifact — revision 0.2.0**

xOSG-0 is a conversational/workflow overlay that turns the documented synthetic-orchestrator design into a concrete, inspectable local workspace.

It maintains five working registers:

- NOTES
- TODO
- ERROR-LOG
- AGENDA
- ROADMAP

It also maintains explicit runtime state, provenance, change-control metadata, and verification state.

## Architecture

1. **Machine Description** — structured configuration and boundaries.
2. **Technical Logic** — invariants and operating rules.
3. **Normal Operating Prompt** — workspace behavior.
4. **Natural-Language Compatibility** — translation of ordinary requests into the existing workflow.
5. **Runtime Workspace** — actual local state and register persistence.
6. **Validation Suite** — repeatable boundary and consistency tests.

The first four layers describe the system. Layers 5–6 make those rules operational without claiming capabilities that are unavailable.

## Core workflow

`INTAKE → DECOMPOSE → ASSIGN → EXECUTE → RECONCILE → VERIFY → DELIVER → LOG`

Execution is capability-gated. A planned action is never represented as completed merely because it was requested.

## Operational boundary

xOSG-0 does **not** modify the underlying model, system instructions, privileges, software configuration, or external accounts. Simulated specialist roles are workflow abstractions unless an actual tool, service, or human is involved.

## Quick start

```text
python runtime/xosg.py init
python runtime/xosg.py status
python runtime/xosg.py task "Describe the task here"
python runtime/xosg.py validate
```

The runtime uses only the local artifact directory and Python's standard library.

## Design principle

> Make state explicit, preserve uncertainty, verify before delivery, and never manufacture capability.

