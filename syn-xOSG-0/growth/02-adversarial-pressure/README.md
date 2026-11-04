# 02 — Adversarial Pressure

## Pressure
Happy-path validation does not reveal whether the runtime survives ambiguity and damage.

## Method
Attack the seed with:
- nulls;
- truncated JSON;
- wrong root types;
- Unicode and control characters;
- repeated operations;
- path-like and shell-like strings;
- oversized and near-valid input.

## Observed failures
Initial fuzzy testing exposed:
- nullable verification causing an AttributeError;
- truncated runtime JSON escaping the validation boundary;
- truncated register JSON escaping the validation boundary.

## Lesson

```text
VALID_INPUT_HANDLING != ROBUST_BOUNDARY_HANDLING
```

## Growth
Failures become regression cases and defensive parsing requirements.

## New pressure
Many individual failures now need to become durable system knowledge.

That produces **03 — Learning Layer**.
