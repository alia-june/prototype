# Repository source boundary

This directory contains the source export of xOSG-0 `MATH.SC-0` v0.8.0.

It is **not a production release**. The module retains its own validation status, authority model, compatibility boundaries, evidence, and production gate.

## Included

- Python numerical and verification plane
- JavaScript contract/control plane and frozen browser surface
- C/C++ native kernel sources and native self-test
- operation contracts, request/result schemas, and failure codes
- tests and build/test evidence
- architecture, authority, interval, numerical-evidence, and hardening documentation

## Intentionally omitted

- `build/` compiled objects, shared libraries, native test binaries, and sanitizer binaries
- Python caches and test caches
- `config/backend_calibration.json`, because calibration is host-specific runtime evidence rather than portable source authority

These omitted artifacts must be regenerated and re-certified on the target host.

## Current development boundary

Abstract logic, sets, relations, predicates, and abstract-object reasoning are outside this module and are deferred to a different machine/module.

The deterministic computation hierarchy remains local compute first, web access only where external fallback is admitted, and LLM reasoning strictly last-resort and non-self-authoritative.
