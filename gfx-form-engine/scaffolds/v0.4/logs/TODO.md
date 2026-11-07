# TODO — v0.3

1. Unicode `\uXXXX` surrogate-pair/scalar validation.
2. Exact matched opener/closer type validation in ELR plane.
3. Streaming/segmented JSON parse boundary state.
4. ELR palette/class table as declarative schema.
5. GPU HIP classification kernel.
6. GPU escape/string scan.
7. GPU structural compaction via rocPRIM.
8. GPU depth/nesting resolution.
9. Plane storage policy interface: dense/sparse/brick selection.
10. Brick hierarchy and empty-region skip.
11. Full DDA initialization/cast traversal, not only step primitive.
12. Cast breadcrumb ring and fault capsules.
13. Recovery-set selection under CPU authority.
14. Continuation spill/checkpoint backing.
15. Frame mapping operations and semantic-projection loss declarations.
16. Windows worker/supervisor implementation.
17. HIP backend implementation and W0 capability probe.
18. Benchmark CPU/GPU crossover and segment sizes.

- T-026 Add generation-aware composition provenance and reconstruction certificates.
- T-027 Add validated Frame graph path resolution across multiple mappings.
- T-028 Add Plane 3 recovery-policy selection through CPU recovery authority.
- T-029 Add recursion checkpoint/continuation spill backing.
- T-030 Add JSON member source-span completion and key/value relationship records.
- T-031 Add JSON Unicode surrogate-pair semantic validation beyond lexical `\\uXXXX` shape.
- T-032 Add ELR bit-packed backing variants and benchmark against byte planes.
- T-033 Add HIP lexical classification kernel behind unvalidated backend boundary.
