# Deterministic Replay and Backend Calibration — MATH.SC-0 v0.7.0

## Replay fingerprints

Every accepted deterministic request receives a SHA-256 `request_fingerprint`. The result receives a separate `result_fingerprint` over the request fingerprint plus computation-defining result fields.

The fingerprints exclude volatile trace/capability timing data. Identical normalized requests and results therefore produce identical fingerprints, allowing logs or a later CLI to detect drift and compare replayed executions.

Current replay format: `0.1.0`.

Fingerprints are integrity/reproducibility identifiers, not cryptographic attestations of machine trust.

## Backend calibration

The worker accepts a local control request:

```json
{"$control":"benchmark","repeats":3,"sizes":[64,1024,16384]}
```

It benchmarks eligible deterministic float64 reduction backends and returns host-specific median/minimum latency observations. The checked-in `config/backend_calibration.json` is a snapshot of the build host and is explicitly marked:

```text
host_specific: true
policy_effect: informational_only
```

Calibration cannot move GPU/native/NumPy/CPU ahead of exactness requirements and cannot move any local backend behind web or LLM authority. It is evidence for later cost modeling, not an authority source.
