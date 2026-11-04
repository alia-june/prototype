# xOSG-0 Loose/Fuzzy Test Report

## Purpose

This suite intentionally tests xOSG-0 with inputs that are semantically vague,
malformed-but-plausible, noisy, multilingual, oversized, repeatedly sequenced,
and partially corrupted. It is complementary to deterministic correctness and
security tests; it is not a proof of correctness.

## Run

- Harness: `validation/fuzzy_test_harness.py`
- Seed: `0x7055E`
- Cases: **58**
- Pass: **55**
- Fail: **2**
- Crash: **1**

## Findings

### FZ-001 — nullable verification object crashes validation

Mutation:

```json
{"verification": null}
```

Observed failure:

`AttributeError: 'NoneType' object has no attribute 'get'`

Expected fuzzy behavior: validation should return a controlled `INVALID`
result with a diagnostic, never an uncaught exception.

### FZ-002 — truncated runtime JSON escapes the validation boundary

The runtime state file was truncated at byte offsets including zero. Validation
raised the JSON decoder exception directly:

`Expecting value: line 1 column 1 (char 0)`

Expected fuzzy behavior: malformed persistence should be reported as
`INVALID`, ideally with a stable diagnostic code, and should not crash callers.

### FZ-003 — truncated register JSON has the same failure mode

The register file produced the same uncaught JSON decoding behavior when
truncated.

Expected fuzzy behavior: controlled `INVALID` result plus corruption
classification.

## Observed strengths

- Empty and whitespace-only objectives did not crash the runtime.
- Unicode and combining characters survived persistence.
- Shell-like and path-like strings were treated as data rather than executed.
- Repeated task/validate/status sequences remained operational.
- Extra register keys were rejected as a register-set mismatch.
- Large tested objectives (up to 4096 characters) remained operational.
- Existing PASS-state compatibility validation continued to function.

## Recommended next hardening target

Add a defensive load/parse boundary that classifies missing, malformed, and
wrong-type JSON as controlled validation failures. Then add a fuzz regression
corpus containing FZ-001 through FZ-003 so these cases cannot regress.
