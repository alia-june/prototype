# MATH.SC-0 JavaScript Front End — v0.5.0

The browser UI is an operator surface, not a mathematical authority. It does not implement numerical kernels in the browser. It submits versioned SC-0 requests to the Node.js boundary, which invokes the existing JavaScript control plane and deterministic Python/native data plane.

## Boundary

Browser JavaScript -> Node HTTP boundary -> JavaScript control plane -> Python data plane -> native/other local backends -> verifier -> optional web -> optional LLM.

The UI exposes result status, backend, verification state, authority, exactness, metadata, and trace so fallback or heuristic results are not visually conflated with verified local computation.

## Start

From `js/`:

```sh
npm run web
```

Default binding: `127.0.0.1:8787`.

Environment overrides:

- `XOSG_SC0_HOST`
- `XOSG_SC0_PORT`
- `PYTHON_BIN`

The default loopback binding is deliberate. Remote exposure should be handled later by an explicit authenticated host layer rather than by changing the computation UI into a network authority surface.
