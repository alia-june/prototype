from xosg_math_sc0 import ComputationEngine, ComputeRequest, NumericMode

engine = ComputationEngine()

for req in [
    ComputeRequest("div", ("1", "3"), mode=NumericMode.EXACT),
    ComputeRequest("sqrt", (2.0,)),
    ComputeRequest("dot", ([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])),
    ComputeRequest("sqrt", ("2",), mode=NumericMode.HIGH_PRECISION, precision=80),
]:
    result = engine.compute(req)
    print(req.operation, "=>", result.value)
    print("  backend:", result.backend, "status:", result.status.value, "verified:", result.verified)
    print("  trace:", " | ".join(result.trace))
