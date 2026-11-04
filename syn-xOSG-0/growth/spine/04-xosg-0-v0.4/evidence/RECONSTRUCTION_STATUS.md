# v0.4 Evidence — Reconstruction Status

The exact historical v0.4 release binary is not currently available in the supplied source set.

The available evidence consists of:

1. the initial 58-case fuzzy suite and its documented failures;
2. the conversation record describing the subsequent hardening cycle;
3. the consolidated v0.5 reconstruction, which contains later deterministic and fuzzy regression harnesses.

## Documented v0.4 endpoint

```text
Loose/fuzzy cases: 107
Passed:            107
Failures:            0
Crashes:             0
Timeouts:            0
```

This count is treated as a documented historical result, not independently recovered binary evidence.

The later consolidated reconstruction expanded the harness further. That later evidence may be staged here only when clearly labeled as reconstruction evidence.

## Developmental significance

v0.4 is where malformed, ambiguous, corrupted, and near-valid input becomes a first-class system concern.

The target semantic is:

```text
uncertain state -> controlled rejection or explicit invalidity
```

rather than crash, hang, silent repair, or fabricated success.
