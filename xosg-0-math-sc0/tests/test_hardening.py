import math
import random
from fractions import Fraction

import mpmath as mp

from xosg_math_sc0 import ComputationEngine, ComputeRequest, NumericMode, ResultStatus
from xosg_math_sc0.linalg import matmul


def iv(lo, hi=None):
    return {"$type": "interval", "lo": str(lo), "hi": str(lo if hi is None else hi)}


def as_mp(q: Fraction):
    return mp.mpf(q.numerator) / q.denominator


def contains(result, x):
    return as_mp(result["lo"]) <= x <= as_mp(result["hi"])


def test_seeded_transcendental_interval_containment():
    rng = random.Random(8012026)
    mp.mp.dps = 100
    e = ComputationEngine()
    cases = []
    for _ in range(20):
        a = rng.uniform(0.01, 8.0); b = a + rng.uniform(0.0, 2.0)
        cases.append(("sqrt", a, b, mp.sqrt))
        cases.append(("log", a, b, mp.log))
        c = rng.uniform(-4.0, 4.0); d = c + rng.uniform(0.0, 2.5)
        cases.append(("exp", c, d, mp.exp))
        cases.append(("sin", c, d, mp.sin))
        cases.append(("cos", c, d, mp.cos))
    for op, a, b, fn in cases:
        r = e.compute(ComputeRequest(op, (iv(repr(a), repr(b)),), mode=NumericMode.INTERVAL, precision=90))
        assert r.status == ResultStatus.VERIFIED, (op, a, b, r.error, r.trace)
        for t in (a, (2*a+b)/3, (a+2*b)/3, b):
            assert contains(r.value, fn(mp.mpf(repr(t)))), (op, a, b, t, r.value)


def test_seeded_interval_sin_cos_wide_ranges_capture_global_extrema():
    e = ComputationEngine()
    for op in ("sin", "cos"):
        r = e.compute(ComputeRequest(op, (iv("-20", "20"),), mode=NumericMode.INTERVAL, precision=80))
        assert r.status == ResultStatus.VERIFIED
        assert r.value["lo"] <= -1
        assert r.value["hi"] >= 1


def test_seeded_exact_inverse_identity_property():
    rng = random.Random(5150)
    e = ComputationEngine()
    checked = 0
    while checked < 20:
        n = rng.choice((2, 3, 4))
        A = [[rng.randint(-5, 5) for _ in range(n)] for _ in range(n)]
        # Make diagonal dominance likely enough to avoid singular retries.
        for i in range(n): A[i][i] += 3*n
        r = e.compute(ComputeRequest("inverse", (A,), mode=NumericMode.EXACT, allow_web=False, allow_llm=False))
        assert r.status == ResultStatus.VERIFIED
        product = matmul(A, r.value, Fraction)
        identity = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
        assert product == identity
        checked += 1


def test_seeded_native_linear_solve_residuals():
    rng = random.Random(9191)
    e = ComputationEngine(native_threshold=1, vector_threshold=10_000_000, accelerator_threshold=10_000_000)
    for n in (2, 3, 4, 6):
        for _ in range(10):
            A = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(n)]
            for i in range(n): A[i][i] += 4*n
            b = [rng.uniform(-10, 10) for _ in range(n)]
            r = e.compute(ComputeRequest("solve", (A, b), mode=NumericMode.FLOAT64, tolerance=1e-10))
            assert r.backend == "native"
            assert r.status == ResultStatus.VERIFIED
            assert r.metadata["verification_residual_inf"] <= r.metadata["verification_threshold"]


def test_exact_arithmetic_metamorphic_distributivity():
    rng = random.Random(31337)
    e = ComputationEngine()
    for _ in range(100):
        a, b, c = (rng.randint(-100, 100) for _ in range(3))
        bc = e.compute(ComputeRequest("add", (b, c), mode=NumericMode.EXACT)).value
        lhs = e.compute(ComputeRequest("mul", (a, bc), mode=NumericMode.EXACT)).value
        ab = e.compute(ComputeRequest("mul", (a, b), mode=NumericMode.EXACT)).value
        ac = e.compute(ComputeRequest("mul", (a, c), mode=NumericMode.EXACT)).value
        rhs = e.compute(ComputeRequest("add", (ab, ac), mode=NumericMode.EXACT)).value
        assert lhs == rhs
