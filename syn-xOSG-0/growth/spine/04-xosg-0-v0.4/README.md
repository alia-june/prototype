# 04 — xOSG-0 v0.4

## Inherited system
xOSG-0 v0.3 deterministic-hardened runtime.

## Pressure
Deterministic tests still assume too much cleanliness.

## Loose/fuzzy pressure
The runtime is challenged with:
- malformed and truncated JSON;
- null structures;
- Unicode and control characters;
- ambiguous input;
- path-like and shell-like strings;
- randomized operation sequences;
- lock and transaction anomalies.

## Target behavior
```text
uncertain state -> controlled rejection or explicit invalidity
```

not silent continuation, crash, or fabricated success.

## Documented validation snapshot
```text
Loose/fuzzy cases: 107
Passed:            107
Failures:            0
Crashes:             0
Timeouts:            0
```

## Next stage
**Seed**
