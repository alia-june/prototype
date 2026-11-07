# How to build and check MATH.SC-0

MATH.SC-0 separates the JavaScript control plane, the Python data plane and verifier, and the native C/C++ kernels. Check them in that order of responsibility when reading a result, and build the native library before running the full suites that exercise it. The [three-runtime architecture](docs/three_runtime_architecture.md) explains the handoffs.

## Choose the check you need

| Check | Prerequisites | What it exercises |
| --- | --- | --- |
| Exact-path smoke check | Node 20 or newer and Python 3.10 or newer | One JavaScript request through the Python worker, returning an exact rational without invoking external fallbacks |
| Native build and self-test | Bash on Linux or macOS, C and C++17 compilers, and the platform linker | Builds the C/C++ shared library and runs the native self-test |
| Full Python suite | Python, `pytest`, `mpmath`, and the built native library for native-dependent cases | Reference computation, dispatch, verification, and numerical and native checks |
| Full JavaScript suite | Node/npm, a Python worker environment, and the numerical dependencies and native library used by integration cases | Control-plane contracts and cross-runtime paths, including native and transcendental interval cases |

The [Python package metadata](pyproject.toml) lists the test, high-precision, and optional NumPy vector dependencies. The [JavaScript package metadata](js/package.json) declares the Node version and test script. Do not interpret a missing dependency or native library as a passing or skipped full validation unless the actual test runner reports it that way.

## Run one exact-path check without a native build

From `xosg-0-math-sc0/`, enter `js/` and run the named existing test:

```sh
cd js
node --test --test-name-pattern="real Python data plane computes exact rational before fallbacks" test/control-plane.test.mjs
```

The worker uses `python` on the command path unless `PYTHON_BIN` points to another interpreter. The test expects `1/3` as an exact fraction and checks that neither its web nor LLM test provider was called. A pass here is a small integration check, not a native or high-precision validation result.

## Build native code, then run the full suites

Return to `xosg-0-math-sc0/`. Use a disposable checkout and a prepared Linux or macOS environment for this sequence. [`scripts/build_native.sh`](scripts/build_native.sh) supports those two host families, defaults to `gcc`/`g++`, and accepts `CC` and `CXX` overrides. The script writes to `build/`, runs the native self-test, and prints the library path. It is not a Windows build script.

```bash
bash scripts/build_native.sh
PYTHONPATH=src python -m pytest -q
cd js
npm test
```

Run each line only after the preceding step succeeds. Keep Node's `PYTHON_BIN` aligned with the prepared Python environment if it differs from the command-path default. The native backend normally looks in the project's build directory; `XOSG_SC0_NATIVE_LIB` can point to an explicitly selected compatible library. Record any override when reporting a result so a successful test can be tied to the library actually loaded.

## Interpret the results

The [project README](README.md#test) reports the retained v0.8.0 verification, including **58 Python tests** and **23 JavaScript/integration tests** passing in its documented environment. Those are release records, not fresh results from this guide.

The [hardening and environment record](docs/hardening_and_walls.md) explains why several claims remain bounded. The recorded host lacked MPFR development headers for an independent compiled directed-rounding oracle and lacked the OpenCL headers and provider needed for an open-compute run. Its accelerator paths were unavailable. The retained transcendental interval implementation uses `mpmath`/libmp; ordinary CPU results do not independently certify that oracle or a GPU backend. Keep an unavailable path, a failed check, and a verified result distinct in any new report.
