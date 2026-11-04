# 01 — Actualization

## Pressure
The seed is coherent but mostly declarative. Its workflow and registers exist conceptually, not as durable runtime objects.

## Added
- persisted runtime state;
- persisted registers;
- runtime schema;
- CLI operations;
- explicit transition history;
- requested-vs-completed action distinction in executable behavior.

## New invariant

```text
DECLARED_STATE should become INSPECTABLE_STATE
```

without implying external execution.

## Evidence
The actualized bare-metal artifact demonstrates this transition.

## New pressure
Once state is executable, malformed state can attack it.

That produces **02 — Adversarial Pressure**.
