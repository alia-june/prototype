# Canonical Growth Spine

This directory describes the primary development path.

```text
ES-xOSG-7
    ↓
xOSG-0 bare-metal 0
    ↓
xOSG-0 v0.2
    ↓
xOSG-0 v0.3
    ↓
xOSG-0 v0.4
    ↓
Seed
```

The sequence is both chronological and developmental.

## Rule

Do not replace this spine with subsystem chronology.

Learning-layer, operator-kernel, operator/orchestrator, deterministic-offload, and goal-scaffolding artifacts are supporting branches and mechanisms. They may explain how a particular version evolved, but they are not the top-level lineage.

## Stage questions

Each stage should answer four things:

1. **Inherited system** — What did this stage receive?
2. **Pressure** — What limitation forced change?
3. **Addition/reduction** — What changed?
4. **Carry-forward** — What survived into the next version?

## End condition

Seed is extracted only after the v0.4 loose/fuzzy hardening stage.

```text
Seed != genesis
Seed != full archive
Seed != release bundle

Seed = minimum justified kernel after the developmental path
```

See `growth/spine/` for the canonical stages.
