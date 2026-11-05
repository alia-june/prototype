# Sanitized Candidate Validation

## Historical result retained

The original package records:

```text
Python 3.12.14 on Linux x86-64
Ran 43 tests
OK
```

The independent intake run observed:

```text
Python 3.14.4 on Windows
Ran 43 tests
FAILED (failures=1)
```

The failure was `test_existing_build_requires_explicit_replace`: expected mode `0644`, observed `0666` after atomic replacement.

## Sanitized suite

The sanitized suite removes only tests whose sole purpose was to open omitted parent, source, generated-build, or vendor-archive payloads. It adds publication-surface checks for excluded payload types and digest receipt structure.

The first sanitized run on Windows with Python 3.14.4 produced:

```text
Ran 36 tests
FAILED (failures=1)
```

The 35 passing tests include both publication-surface checks. The sole failure is the same retained mode-preservation defect described above. `python -B assembler.py --list` also completed successfully and exposed all 11 profiles and 17 modules.

A passing publication-surface check does not erase the retained Windows portability failure.

## Limits

No named model was tested against the behavioral vectors. No live security boundary, external control plane, secrets manager, replay store, trusted clock, or vendor engine is supplied. Static assembly tests cannot prove prompt-injection immunity, mission stability, legal compliance, semantic correctness, or production safety.

