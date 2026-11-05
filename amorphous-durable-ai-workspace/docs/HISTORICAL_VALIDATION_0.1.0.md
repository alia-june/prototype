# Validation Report — Durable Workspace Development Kit v0.1.0

Date: 2026-09-28

## Results

- Python unit suite: **9/9 PASS**.
- Package destructive/self-validation: **7/7 PASS**.
- Python source compileall: **PASS**.
- Example create/checkpoint/recover flow: **PASS**.
- Wheel build using `pip wheel --no-deps --no-build-isolation`: **PASS**.
- Isolated wheel install/import/mutate/verify smoke test: **PASS**.

## Destructive/self-validation coverage

- initial runtime integrity and journal verification;
- four concurrent writer processes / 200 committed mutations;
- published three-representation snapshot verification;
- recovery with SQLite representation damaged;
- recovery with JSONL representation damaged;
- recovery with XML representation damaged;
- runtime journal hash-chain tamper detection.

## Unit coverage highlights

- Unicode NFC normalization and deterministic object-key ordering;
- float rejection under DWSK-CJ-1;
- set/get/delete transaction + journal behavior;
- exact SQLite/JSONL/XML logical equivalence;
- control characters and unusual record keys through base64-safe XML strings/keys;
- 2-of-3 recovery quorum;
- refusal to auto-recover from a single surviving representation;
- refusal when the published manifest logical digest disagrees with the surviving quorum.

This report validates the supplied implementation and fixtures; it is not a proof against all filesystem, kernel, power-loss, or storage-device failure modes.

Embedded wheel SHA-256: `477b6969b2bba72a8ae0e64c4e4ec9ce2556d5dd64c541348eaae893a9c63c57`
