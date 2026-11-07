# Build Report — v0.9

Date: 2026-10-07

## Validation
- CMake configure: PASS
- C++20 build: PASS
- Compiler warnings in build output: none observed
- CTest: 38/38 PASS
- Existing 5,000-level iterative JSON nesting test: PASS

## Added this increment
- Portable SHA-256 `Digest256` implementation and known-vector test.
- SHA-256-backed integrity commit chain over committed ledger evidence.
- Recovery plan validation across checkpoint, route, recovery domain, frame, transaction, generation and activation membership.
- Separate explicit recovery authorization step.
- Cross-frame cast resolution through explicit frame graph/mapping chain before aligned plane reads.
- Immutable generation-bound JSON mutation/reparse contract.
- ELR rebuild request after source mutation.

## Boundaries
- SHA-256 integrity does not provide signer authenticity, trusted timestamping or durable crash consistency.
- HIP/RX 7700 XT execution remains unvalidated on target hardware.
- Win32 worker/supervisor and durable FlushFileBuffers commit protocol remain unvalidated.
- Exact bitcodes and packed binary layouts remain intentionally unfrozen.
