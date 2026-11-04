# xOSG-0 Complete Chat Artifact — v0.5.0

## Expert Overlay System Gestalt — Version Bare-Metal 0

This package consolidates the xOSG-0 development work represented in the current chat into one inspectable release.

It contains:

- the exact historical archives still available from the chat;
- unpacked copies of those historical artifacts;
- the four original descriptive layers;
- a newly consolidated hardened local runtime;
- runtime-state and register schemas;
- deterministic hardening tests;
- an expanded loose/fuzzy harness;
- captured validation reports;
- a visible conversation transcript;
- a normal chat summary;
- a technical chat summary;
- artifact-lineage documentation;
- SHA-256 integrity manifests.

## System boundary

xOSG-0 is a **synthetic orchestration/workspace overlay**. It does not modify the underlying model, grant itself privileges, access external accounts without an actual integration, spawn hidden human experts, or turn a requested action into a completed action merely because it was requested.

## Architecture

1. Machine Description
2. Technical Logical Instrumentation
3. Normal Text Operating Prompt
4. Natural-Language Compatibility
5. Runtime Workspace
6. Validation and Fuzzing

## Five registers

`NOTES` · `TODO` · `ERROR-LOG` · `AGENDA` · `ROADMAP`

## Core workflow

```text
INTAKE → DECOMPOSE → ASSIGN → EXECUTE → RECONCILE → VERIFY → DELIVER → LOG
```

## Quick start

```bash
python runtime/xosg.py init
python runtime/xosg.py status
python runtime/xosg.py task "Describe the task"
python runtime/xosg.py validate
python runtime/xosg.py recover
```

## Run deterministic tests

```bash
python validation/test_hardening.py
```

Expected packaged release result: **50/50 passed**.

## Run loose/fuzzy tests

```bash
python validation/fuzzy_test_harness.py
```

Expected packaged release result: **206/206 passed, 0 failures, 0 crashes, 0 timeouts**.

## Read the conversation material

- `docs/VISIBLE_CHAT_TRANSCRIPT.md`
- `docs/CHAT_SUMMARY.md`
- `docs/TECHNICAL_CHAT_SUMMARY.md`
- `docs/ARTIFACT_LINEAGE.md`

## Integrity

See `manifests/SHA256SUMS.txt` and `manifests/RELEASE_MANIFEST.json`.
