# AI Error Log — v0.5

- Historical: META terminology was over-promoted; corrected to Abstraction / Abstract Forms.
- Historical: large structures were too close to roots; corrected to molecular compositions.
- Historical: three separate casts were proposed; corrected to one 3D cast + aligned reads.
- Historical: fixed recursion depth was proposed; corrected to Plane-3 dynamic governance.
- Historical: axis semantics were over-concretized; corrected to frame-scoped generic XYZ.
- Historical: initial JSON parser draft used native recursive descent; replaced before packaging with explicit iterative context stack and 5,000-level nesting test.
- AIERR-007 — Iterative parser close-object path referenced context after `stack.pop_back()`. Corrected by capturing required values before pop; suite rebuilt cleanly.
- AIERR-008 — v0.5 CMake test-block generation inserted the new test targets into both the compiler-options `if` and `BUILD_TESTING` block by replacing every `endif()`. Corrected by rewriting CMakeLists with one explicit test list; 16/16 tests pass.
