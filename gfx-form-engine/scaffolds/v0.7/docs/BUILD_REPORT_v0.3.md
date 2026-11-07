# Build Report v0.3

- Host validation: Linux C++20 reference build
- Configure: PASS
- Compile: PASS with warning-clean project sources
- Tests: 8/8 PASS
- Deep recursion-form test: 5,000 nested arrays PASS using explicit iterative context stack
- HIP backend: scaffold only / NOT VALIDATED
- Windows GPU supervisor: interface only / NOT VALIDATED
- RX 7700 XT behavior: NOT VALIDATED on hardware in this build

## Newly validated in v0.3
- strict UTF-8 rejection
- JSON number grammar
- JSON spans/data/nodes/sequencing
- frame/generation-aligned tri-plane reads
- cast trace construction
- no native recursive descent dependency for deep JSON structure
