import math
import random

from xosg_math_sc0 import ComputationEngine, ComputeRequest, NumericMode, ResultStatus


def _engine():
    return ComputationEngine(native_threshold=1, vector_threshold=10_000_000, accelerator_threshold=10_000_000)


def test_native_sum_differential_seeded():
    rng = random.Random(1337)
    e = _engine()
    for _ in range(40):
        values = [rng.uniform(-1e4, 1e4) for _ in range(rng.randint(2, 80))]
        r = e.compute(ComputeRequest("sum", (values,), mode=NumericMode.FLOAT64, tolerance=1e-11))
        assert r.backend == "native"
        assert r.status == ResultStatus.VERIFIED
        assert math.isclose(r.value, math.fsum(values), rel_tol=1e-11, abs_tol=1e-11)


def test_native_dot_differential_seeded():
    rng = random.Random(7331)
    e = _engine()
    for _ in range(30):
        n = rng.randint(2, 64)
        a = [rng.uniform(-100, 100) for _ in range(n)]
        b = [rng.uniform(-100, 100) for _ in range(n)]
        expected = math.fsum(x * y for x, y in zip(a, b, strict=True))
        r = e.compute(ComputeRequest("dot", (a, b), mode=NumericMode.FLOAT64, tolerance=1e-11))
        assert r.backend == "native"
        assert r.status == ResultStatus.VERIFIED
        assert math.isclose(r.value, expected, rel_tol=1e-11, abs_tol=1e-11)


def test_native_vector_binary_differential_seeded():
    rng = random.Random(2026)
    e = _engine()
    for operation in ("add", "sub", "mul"):
        a = [rng.uniform(-50, 50) for _ in range(32)]
        b = [rng.uniform(-50, 50) for _ in range(32)]
        r = e.compute(ComputeRequest(operation, (a, b), mode=NumericMode.FLOAT64, tolerance=1e-12))
        assert r.backend == "native"
        assert r.status == ResultStatus.VERIFIED


def test_native_matmul_differential_seeded():
    rng = random.Random(9001)
    e = _engine()
    for rows, inner, cols in ((2, 2, 2), (3, 4, 2), (4, 3, 5)):
        a = [[rng.uniform(-10, 10) for _ in range(inner)] for _ in range(rows)]
        b = [[rng.uniform(-10, 10) for _ in range(cols)] for _ in range(inner)]
        r = e.compute(ComputeRequest("matmul", (a, b), mode=NumericMode.FLOAT64, tolerance=1e-11))
        assert r.backend == "native"
        assert r.status == ResultStatus.VERIFIED


def test_native_det_solve_inverse_differential_seeded():
    import numpy as np
    rng = random.Random(424242)
    e = _engine()
    for n in (2, 3, 5):
        for _ in range(8):
            # Diagonal dominance keeps this differential test away from intended
            # singular/ill-conditioned cases; those are tested separately.
            a = [[rng.uniform(-2, 2) for _ in range(n)] for _ in range(n)]
            for i in range(n):
                a[i][i] += 3.0 * n
            b = [rng.uniform(-3, 3) for _ in range(n)]
            rd = e.compute(ComputeRequest("det", (a,), mode=NumericMode.FLOAT64, tolerance=1e-9))
            rs = e.compute(ComputeRequest("solve", (a, b), mode=NumericMode.FLOAT64, tolerance=1e-9))
            ri = e.compute(ComputeRequest("inverse", (a,), mode=NumericMode.FLOAT64, tolerance=1e-9))
            assert rd.backend == rs.backend == ri.backend == "native"
            assert rd.status == rs.status == ri.status == ResultStatus.VERIFIED
            assert math.isclose(rd.value, float(np.linalg.det(np.asarray(a))), rel_tol=1e-9, abs_tol=1e-9)
            assert np.allclose(np.asarray(rs.value), np.linalg.solve(np.asarray(a), np.asarray(b)), rtol=1e-9, atol=1e-9)
            assert np.allclose(np.asarray(ri.value), np.linalg.inv(np.asarray(a)), rtol=1e-9, atol=1e-9)
