# 05 — Seed

## Inherited system
The surviving structure of xOSG-0 after bare-metal reduction, actualization, deterministic hardening, and loose/fuzzy hardening.

## Definition
Seed is the smallest coherent reusable kernel justified by the full development path.

```text
ES-xOSG-7
 -> xOSG-0 bare-metal
 -> v0.2
 -> v0.3
 -> v0.4
 -> SEED
```

## Admission criteria
A component belongs in Seed only if it is:
- necessary;
- explicit;
- bounded;
- testable;
- provenance-traceable;
- non-redundant;
- supported by developmental evidence.

## Seed is not
- the archive;
- every experimental subsystem;
- the full release history;
- every prompt or implementation detail.

## Seed is
```text
surviving invariants
+ minimum mechanisms
+ explicit boundaries
+ regression obligations
```

Seed is the endpoint of this lineage and may become the genesis of a future system.
