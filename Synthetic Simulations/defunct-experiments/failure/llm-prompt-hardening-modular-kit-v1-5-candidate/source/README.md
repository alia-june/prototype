# Modular LLM Continuity and Mission-Control Prompt Kit

## Defunct experiment, sanitized publication candidate

This directory is a publication-oriented source reduction of candidate 1.5, prepared from the archived intake without promoting the experiment or rewriting its result.

**Historical status:** failed portability validation. The original package reported 43/43 tests passing on Linux with Python 3.12.14. An independent run on Windows with Python 3.14.4 passed 42/43 tests; `test_existing_build_requires_explicit_replace` observed mode `0666` where the test required `0644`.

That failure is intentionally preserved. This candidate does not claim acceptance, production readiness, behavioral immunity, or a corrected implementation.

## What is included

- `assembler.py` and `config.json`
- the 17 modular prompt fragments
- templates and selection heuristics
- behavioral test vectors
- the substantive regression suite, with payload-preservation tests removed because the payloads are not distributed
- generated historical audits under `docs/historical/`
- digest receipts for omitted evidence and dependencies

## What is excluded

- nested candidate and parent archives
- supplied DOCX and research/source payloads
- the optional vendor engine archive
- generated prompt builds, which can be reproduced from the assembler
- bytecode, historical engine runs, logs, caches, and temporary artifacts

The exclusions are deliberate publication sanitation, not evidence that the omitted material was invalid. `SOURCE_RECEIPTS.json` preserves the exact identifiers and SHA-256 values needed to correlate this source reduction with the original intake.

## Use

List profiles and modules:

```shell
python assembler.py --list
```

Generate a new inert template:

```shell
python assembler.py --profile standard --output builds/runtime_standard.md
```

Run the retained tests:

```shell
python -m unittest discover -s tests -v
```

The sanitized Windows run passed 35/36 tests. The sole failure is the retained
POSIX mode-portability defect described above; both publication-surface tests
passed.

All generated templates remain inert while required values are unresolved. Prompt text is a behavior-shaping control, not a security boundary.

## Publication status

The project-owned source is published under the MIT License by explicit user authorization dated 2026-11-01. This repository remains private; publication here means admitted to the controlled OpenSurface publishing tree, not made publicly visible.

The optional engine is separately identified as MIT-licensed by m.A.R.S. and is not bundled here. See `THIRD_PARTY_NOTICES.md` for its preserved notice.

