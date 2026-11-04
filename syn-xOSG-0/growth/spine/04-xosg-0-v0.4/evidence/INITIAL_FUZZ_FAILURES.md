# Initial Loose/Fuzzy Failure Record

The first loose/fuzzy pass intentionally tested semantically vague, malformed-but-plausible, noisy, multilingual, oversized, repeatedly sequenced, and partially corrupted inputs.

## Initial result

```text
Cases: 58
Pass: 55
Fail: 2
Crash: 1
```

## Findings

### FZ-001 — nullable verification object

Mutation:

```json
{"verification": null}
```

Observed behavior: an attribute-access exception escaped validation.

Required behavior: controlled `INVALID` classification with a diagnostic.

### FZ-002 — truncated runtime JSON

Truncated runtime state escaped the validation boundary as a JSON decoding exception.

Required behavior: controlled invalidity with corruption classification.

### FZ-003 — truncated register JSON

Truncated register persistence produced the same uncontrolled parsing class.

Required behavior: controlled invalidity with corruption classification.

## Why this matters

These failures are the pressure that justifies the later v0.4 fail-closed behavior. The point of the fuzzy stage is not merely a larger test count; it is to turn malformed-state behavior into explicit system semantics.
