# Strmdocx corrected-harness product-retest findings

Date: 2026-10-31. AUTH-19C-A. Result: **no current product defect established**.

## Service result

Service harness `docstream.harness/1.3` passes its complete retained workload
against product version `0.2.0.dev4`:

- 119 rigid regression cases pass;
- 500 deterministic fuzzy cases pass;
- five torture scenarios pass;
- 24 render calls and 1,907 torture service calls complete;
- all three owned mode workers use assignment-before-resume, report confirmed
  cleanup and finish with job active count zero;
- the independent service-run auditor returns no issue;
- no product file is reported changed.

The service result does not reproduce the historical HF-01/HF-02/HF-03 product
groups or the later Windows cleanup failures. Those histories remain retained;
the current pass does not rewrite them.

## Native result

Native harness `docstream.native-harness/1.1` passes:

- 100 hardening cases: 84 exact-error cases and 16 probes;
- 1,000 fuzzy-error cases: 800 exact expected rejections and 200 valid controls;
- eight torture scenarios;
- 1,520 submitted transformation attempts.

Every fuzzy expected rejection records `NativeError`, a concrete expected code,
`expected_rejection: true` and `state_fingerprint_unchanged: true`. All three
audited native mode summaries have zero audit issues and zero interrupted cases.
The product hash sets before and after are identical, and no changed product file
is reported.

## Finding classification

AUTH-19C-A establishes a current passing observation under these bounded
workloads. It does not establish that the product is universally defect-free,
that untested foreign formats are supported, that GPU lowering is correct, or
that production capacity and security have been certified.

Most importantly, the run does not provide a defect to repair. Editing product
source merely to satisfy the phrase "fix Strmdocx" would invent a change without
an observed failure, replay or acceptance criterion. No AUTH-19C-B product
repair is justified by this evidence.

## Lessons and anti-lessons

- Repair the verifier before trusting its product findings.
- Re-run the product after a harness repair; do not assume that a clean unit-test
  discovery is equivalent to the maintained workload suite.
- Exact expected exceptions and unchanged complete state are stronger evidence
  than a generic rejection count.
- A historical failure remains historical evidence even when its current replay
  passes.
- Passing bounded workloads do not prove universal correctness or production
  capacity.
- Do not manufacture a product change when the corrected harness supplies no
  failing input.

## Next boundary

AUTH-19C-A is a validation result, not release or integration approval. GPU work,
full WordNet/Etabit transmigration, live service registration, release and
agentic-control integration remain outside this scope. Agentic integration
remains last.
