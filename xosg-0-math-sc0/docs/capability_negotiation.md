# Backend Capability Negotiation — MATH.SC-0 v0.8.0

Capability protocol: `0.3.0`.

The Python data plane exposes an ordered backend manifest. Each backend reports availability, policy priority, operation claims, request eligibility, and cost hints where applicable. Capability data may affect eligibility but never authority order.

Current deterministic order:

```text
exact -> high_precision -> interval -> accelerator -> open_compute -> native -> numpy -> cpu
```

Native capability claims now include determinant, solve, and inverse. When the native library is loaded the manifest also exposes its ABI version.

The JavaScript control plane can query the Python worker with:

```json
{"$control":"capabilities"}
```

Current host limitations are reported honestly: the Torch accelerator is unavailable because the installed build is CPU-only; the open-compute adapter has no attached provider unless the operator supplies one.
