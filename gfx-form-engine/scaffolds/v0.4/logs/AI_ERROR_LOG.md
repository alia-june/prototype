# AI Error Log — v0.3

- Historical: META terminology was over-promoted; corrected to Abstraction / Abstract Forms.
- Historical: large structures were too close to roots; corrected to molecular compositions.
- Historical: three separate casts were proposed; corrected to one 3D cast + aligned reads.
- Historical: fixed recursion depth was proposed; corrected to Plane-3 dynamic governance.
- Historical: axis semantics were over-concretized; corrected to frame-scoped generic XYZ.
- v0.3 construction correction: an initial JSON parser draft used native recursive descent. It was replaced before packaging with an explicit iterative context stack and a 5000-level nesting test.

## AIERR-007 — Iterative parser context lifetime after pop
During v0.4 compilation, the compiler identified a close-object path that accessed the current parser context after `stack.pop_back()`. That reference could be invalidated.

**Correction:** capture the closed node identity and opening offset before popping, then use the captured values. Rebuilt with warning removed; full suite passed.
