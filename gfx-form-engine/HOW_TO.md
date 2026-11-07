# How to build the GFX Form Engine CPU scaffold

Use this guide to configure, build, and test the **v0.9 CPU scaffold**. The repository also retains earlier scaffold snapshots and a research architecture. Choose the version before building so the result can be traced to a specific source tree.

## Select the scaffold and toolchain

- Start in `gfx-form-engine/` in a disposable checkout or review workspace.
- Have CMake **3.20 or newer**, CTest, and a working **C++20** compiler and generator available in the shell. On Windows, use a shell configured for the compiler and generator you intend to use.
- Use [`scaffolds/v0.9/`](scaffolds/v0.9/). Its [`CMakeLists.txt`](scaffolds/v0.9/CMakeLists.txt) defines the CPU library, smoke executable, and test targets. The CPU path does not require HIP.

## Configure, build, and test

Run the commands in order. Use a fresh build directory if you previously configured a different compiler or generator.

```sh
cd scaffolds/v0.9
cmake -S . -B build-cpu -DGFX_ENABLE_HIP=OFF -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build-cpu --config Debug
ctest --test-dir build-cpu -C Debug --output-on-failure
```

The `CMAKE_BUILD_TYPE` option selects Debug for single-configuration generators; `--config Debug` and `-C Debug` select it for multi-configuration build and test commands. Build output goes to `build-cpu/`, separate from the scaffold source.

If configuration cannot find a compiler, resolve the toolchain issue before trying to run tests. If CTest finds no tests, check that you configured this scaffold with `BUILD_TESTING=ON` and pointed CTest at the corresponding build directory. A build completing without a CTest run is not a test pass.

## Read the result within its scope

The [recorded v0.9 build report](scaffolds/v0.9/docs/BUILD_REPORT_v0.9.md) records **38/38 CPU tests passing**, including an iterative parse of 5,000 nested arrays. That example exercises the parser's explicit stack; it is not a universal depth limit. Compare your run with the recorded scaffold version and retain the compiler, generator, and failing test output if they differ.

This route does not exercise the intended Windows/Radeon/HIP target, Windows worker supervision, or durable commit and recovery. A digest chain can expose integrity discrepancies without authenticating a signer or demonstrating crash durability. See the [architecture guide](ARCHITECTURE.md) for how frames, forms, aligned reads, and recovery fit together. The commands here are the documented CPU build path, not a new build result.
