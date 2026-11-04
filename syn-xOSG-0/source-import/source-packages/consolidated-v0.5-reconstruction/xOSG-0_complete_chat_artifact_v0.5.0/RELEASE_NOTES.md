# Release Notes — v0.5.0

This is the first **complete-conversation consolidation release**.

The release is deliberately provenance-aware. It does not pretend that missing historical v0.3/v0.4 ZIPs are available. Instead it preserves the original, v0.2.0, and initial-fuzzy historical archives exactly as present, then provides a new hardened v0.5.0 implementation that realizes the later requirements from the chat.

## Verified packaged results

- Deterministic suite: 50 passed, 0 failed.
- Loose/fuzzy suite: 206 passed, 0 failed, 0 crashed, 0 timed out.
- Python compilation: pass.
- CLI help smoke test: pass.
- Clean workspace validation: pass.

## Principal hardening properties

- fail-closed corruption handling;
- no raw nested access before type validation;
- atomic file replacement;
- paired transaction journal for state + registers;
- checksum-validated recovery;
- bounded mutation lock;
- stale lock recovery;
- symlink refusal;
- bounded task/state sizes;
- explicit transition constraints;
- deterministic fuzz regression coverage.
