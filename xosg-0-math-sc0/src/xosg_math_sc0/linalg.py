from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable


def determinant(matrix: list[list[Any]], convert: Callable[[Any], Any]) -> Any:
    a = [[convert(x) for x in row] for row in matrix]
    n = _check_square(a)
    sign = 1
    det = convert(1)
    for col in range(n):
        pivot = _pivot_row(a, col, col)
        if pivot is None:
            return convert(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign = -sign
        pv = a[col][col]
        det *= pv
        for row in range(col + 1, n):
            if a[row][col] == 0:
                continue
            factor = a[row][col] / pv
            a[row][col] = convert(0)
            for j in range(col + 1, n):
                a[row][j] -= factor * a[col][j]
    return -det if sign < 0 else det


def solve(matrix: list[list[Any]], rhs: list[Any] | list[list[Any]], convert: Callable[[Any], Any]) -> Any:
    a = [[convert(x) for x in row] for row in matrix]
    n = _check_square(a)
    rhs_is_matrix = bool(rhs) and isinstance(rhs[0], (list, tuple))
    if rhs_is_matrix:
        b = [[convert(x) for x in row] for row in rhs]
        if len(b) != n:
            raise ValueError("right-hand matrix row count mismatch")
        m = len(b[0]) if b else 0
        if m < 1 or any(len(row) != m for row in b):
            raise ValueError("right-hand matrix must be rectangular and non-empty")
    else:
        if len(rhs) != n:
            raise ValueError("right-hand vector length mismatch")
        b = [[convert(x)] for x in rhs]
        m = 1

    # Gauss-Jordan elimination with partial pivoting. For exact Fractions,
    # pivot choice affects cost but not the exact result. For floats, maximum
    # absolute pivoting materially improves stability over naive elimination.
    for col in range(n):
        pivot = _pivot_row(a, col, col)
        if pivot is None:
            raise ArithmeticError("singular matrix")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            b[col], b[pivot] = b[pivot], b[col]
        pv = a[col][col]
        if pv == 0:
            raise ArithmeticError("singular matrix")
        inv = convert(1) / pv
        for j in range(col, n):
            a[col][j] *= inv
        for j in range(m):
            b[col][j] *= inv
        for row in range(n):
            if row == col:
                continue
            factor = a[row][col]
            if factor == 0:
                continue
            a[row][col] = convert(0)
            for j in range(col + 1, n):
                a[row][j] -= factor * a[col][j]
            for j in range(m):
                b[row][j] -= factor * b[col][j]
    if rhs_is_matrix:
        return b
    return [row[0] for row in b]


def inverse(matrix: list[list[Any]], convert: Callable[[Any], Any]) -> list[list[Any]]:
    n = _check_square(matrix)
    identity = [[convert(1 if i == j else 0) for j in range(n)] for i in range(n)]
    return solve(matrix, identity, convert)


def matmul(left: list[list[Any]], right: list[list[Any]], convert: Callable[[Any], Any]) -> list[list[Any]]:
    if not left or not right or not left[0] or not right[0]:
        raise ValueError("matmul requires non-empty matrices")
    if any(len(row) != len(left[0]) for row in left) or any(len(row) != len(right[0]) for row in right):
        raise ValueError("matrices must be rectangular")
    if len(left[0]) != len(right):
        raise ValueError("matmul dimension mismatch")
    cols = list(zip(*right, strict=True))
    zero = convert(0)
    return [[sum((convert(x) * convert(y) for x, y in zip(row, col, strict=True)), zero) for col in cols] for row in left]


def dot(left: list[Any], right: list[Any], convert: Callable[[Any], Any]) -> Any:
    if len(left) != len(right):
        raise ValueError("dot requires equal-length vectors")
    zero = convert(0)
    return sum((convert(x) * convert(y) for x, y in zip(left, right, strict=True)), zero)


def residual_inf_norm(matrix, solution, rhs) -> float:
    """Infinity norm of A*x-b (or A*X-B), evaluated in float64 for diagnostics."""
    import math
    rhs_matrix = bool(rhs) and isinstance(rhs[0], (list, tuple))
    sol_matrix = bool(solution) and isinstance(solution[0], (list, tuple))
    if rhs_matrix != sol_matrix:
        return math.inf
    if rhs_matrix:
        ax = matmul(matrix, solution, float)
        return max((abs(float(ax[i][j]) - float(rhs[i][j])) for i in range(len(rhs)) for j in range(len(rhs[0]))), default=0.0)
    vals = []
    for row, bi in zip(matrix, rhs, strict=True):
        s = sum(float(x) * float(y) for x, y in zip(row, solution, strict=True))
        vals.append(abs(s - float(bi)))
    return max(vals, default=0.0)


def inverse_residual_inf_norm(matrix, inv) -> float:
    import math
    prod = matmul(matrix, inv, float)
    n = len(matrix)
    return max((abs(float(prod[i][j]) - (1.0 if i == j else 0.0)) for i in range(n) for j in range(n)), default=0.0)


def _check_square(matrix) -> int:
    if not isinstance(matrix, (list, tuple)) or not matrix:
        raise ValueError("matrix must be non-empty")
    n = len(matrix)
    if any(not isinstance(row, (list, tuple)) or len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    return n


def _pivot_row(a, start: int, col: int):
    candidates = [(abs(a[i][col]), i) for i in range(start, len(a)) if a[i][col] != 0]
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


def as_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"not exact-compatible: {type(value).__name__}")
