from __future__ import annotations

import ctypes
import math
import os
import platform
from pathlib import Path
from typing import Iterable

from .base import Backend
from ..types import ComputeRequest, ComputeResult, NumericMode, ResultStatus


_BINARY = {"add": 1, "sub": 2, "mul": 3, "div": 4, "pow": 5}
_UNARY = {"sqrt": 1, "exp": 2, "log": 3, "sin": 4, "cos": 5, "tan": 6}
_VECTOR = {"add", "sub", "mul"}
_REDUCE = {"sum", "mean", "norm", "dot", "matmul", "det", "solve", "inverse"}


class NativeBackend(Backend):
    """ctypes adapter for the compiled C/C++ deterministic kernel library."""

    name = "native"

    def __init__(self, threshold: int = 64, library_path: str | None = None):
        self.threshold = threshold
        self.library_path = library_path or os.getenv("XOSG_SC0_NATIVE_LIB") or str(_default_library())
        self.lib = None
        self.load_error: str | None = None
        try:
            path = Path(self.library_path)
            if path.exists():
                self.lib = ctypes.CDLL(str(path))
                self._configure()
            else:
                self.load_error = f"native library not found: {path}"
        except Exception as exc:  # pragma: no cover - host loader failures vary
            self.load_error = f"{type(exc).__name__}: {exc}"
            self.lib = None

    def _configure(self) -> None:
        c_double_p = ctypes.POINTER(ctypes.c_double)
        self.lib.sc0_native_version.argtypes = []
        self.lib.sc0_native_version.restype = ctypes.c_char_p
        self.lib.sc0_binary_scalar.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, c_double_p]
        self.lib.sc0_binary_scalar.restype = ctypes.c_int
        self.lib.sc0_unary_scalar.argtypes = [ctypes.c_int, ctypes.c_double, c_double_p]
        self.lib.sc0_unary_scalar.restype = ctypes.c_int
        self.lib.sc0_sum.argtypes = [c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_sum.restype = ctypes.c_int
        self.lib.sc0_mean.argtypes = [c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_mean.restype = ctypes.c_int
        self.lib.sc0_norm.argtypes = [c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_norm.restype = ctypes.c_int
        self.lib.sc0_dot.argtypes = [c_double_p, c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_dot.restype = ctypes.c_int
        self.lib.sc0_vec_binary.argtypes = [ctypes.c_int, c_double_p, c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_vec_binary.restype = ctypes.c_int
        self.lib.sc0_matmul.argtypes = [
            c_double_p, ctypes.c_size_t, ctypes.c_size_t,
            c_double_p, ctypes.c_size_t, ctypes.c_size_t,
            c_double_p,
        ]
        self.lib.sc0_matmul.restype = ctypes.c_int
        self.lib.sc0_det.argtypes = [c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_det.restype = ctypes.c_int
        self.lib.sc0_solve.argtypes = [c_double_p, ctypes.c_size_t, c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_solve.restype = ctypes.c_int
        self.lib.sc0_inverse.argtypes = [c_double_p, ctypes.c_size_t, c_double_p]
        self.lib.sc0_inverse.restype = ctypes.c_int

    def available(self) -> bool:
        return self.lib is not None

    def supports(self, request: ComputeRequest) -> bool:
        if not self.available() or request.mode in {NumericMode.EXACT, NumericMode.HIGH_PRECISION}:
            return False
        op = request.operation
        if op not in set(_BINARY) | set(_UNARY) | _REDUCE:
            return False
        # Scalar ctypes calls are deliberately not selected by default; the native
        # plane becomes worthwhile at sufficient vector/matrix work size.
        return _work_size(request.operands) >= self.threshold

    def cost_hint(self, request: ComputeRequest) -> float:
        return 0.2

    def compute(self, request: ComputeRequest) -> ComputeResult:
        op, a = request.operation, request.operands
        if op in _BINARY and _is_scalar_pair(a):
            out = ctypes.c_double()
            self._check(self.lib.sc0_binary_scalar(_BINARY[op], float(a[0]), float(a[1]), ctypes.byref(out)), op)
            value = out.value
        elif op in _UNARY:
            out = ctypes.c_double()
            self._check(self.lib.sc0_unary_scalar(_UNARY[op], float(a[0]), ctypes.byref(out)), op)
            value = out.value
        elif op in _VECTOR:
            left = _vector(a[0]); right = _vector(a[1])
            if len(left) != len(right):
                raise ValueError("native vector operands must have equal length")
            la = _array(left); ra = _array(right); out_arr = (ctypes.c_double * len(left))()
            self._check(self.lib.sc0_vec_binary(_BINARY[op], la, ra, len(left), out_arr), op)
            value = list(out_arr)
        elif op in {"sum", "mean", "norm"}:
            values = _vector(a[0]); arr = _array(values); out = ctypes.c_double()
            fn = {"sum": self.lib.sc0_sum, "mean": self.lib.sc0_mean, "norm": self.lib.sc0_norm}[op]
            self._check(fn(arr, len(values), ctypes.byref(out)), op)
            value = out.value
        elif op == "dot":
            left = _vector(a[0]); right = _vector(a[1])
            if len(left) != len(right):
                raise ValueError("native dot operands must have equal length")
            la = _array(left); ra = _array(right); out = ctypes.c_double()
            self._check(self.lib.sc0_dot(la, ra, len(left), ctypes.byref(out)), op)
            value = out.value
        elif op == "matmul":
            left, lr, lc = _matrix(a[0])
            right, rr, rc = _matrix(a[1])
            if lc != rr:
                raise ValueError(f"native matmul shape mismatch: {lr}x{lc} @ {rr}x{rc}")
            la = _array(left); ra = _array(right); out_arr = (ctypes.c_double * (lr * rc))()
            self._check(self.lib.sc0_matmul(la, lr, lc, ra, rr, rc, out_arr), op)
            flat = list(out_arr)
            value = [flat[i * rc:(i + 1) * rc] for i in range(lr)]
        elif op == "det":
            flat, rows, cols = _matrix(a[0])
            if rows != cols: raise ValueError("native det requires square matrix")
            arr = _array(flat); out = ctypes.c_double()
            self._check(self.lib.sc0_det(arr, rows, ctypes.byref(out)), op)
            value = out.value
        elif op == "solve":
            flat, rows, cols = _matrix(a[0])
            if rows != cols: raise ValueError("native solve requires square matrix")
            rhs_is_matrix = bool(a[1]) and isinstance(a[1][0], (list, tuple))
            if rhs_is_matrix:
                rhs_flat, rr, rc = _matrix(a[1])
                if rr != rows: raise ValueError("native solve rhs row mismatch")
                rhs_cols = rc
            else:
                rhs_flat = _vector(a[1]); rhs_cols = 1
                if len(rhs_flat) != rows: raise ValueError("native solve rhs length mismatch")
            aa = _array(flat); bb = _array(rhs_flat); out_arr = (ctypes.c_double * (rows * rhs_cols))()
            self._check(self.lib.sc0_solve(aa, rows, bb, rhs_cols, out_arr), op)
            out_flat = list(out_arr)
            value = ([out_flat[i] for i in range(rows)] if rhs_cols == 1 else [out_flat[i*rhs_cols:(i+1)*rhs_cols] for i in range(rows)])
        elif op == "inverse":
            flat, rows, cols = _matrix(a[0])
            if rows != cols: raise ValueError("native inverse requires square matrix")
            arr = _array(flat); out_arr = (ctypes.c_double * (rows * rows))()
            self._check(self.lib.sc0_inverse(arr, rows, out_arr), op)
            out_flat = list(out_arr)
            value = [out_flat[i*rows:(i+1)*rows] for i in range(rows)]
        else:
            raise ValueError(f"unsupported native operation: {op}")

        if not _finite(value):
            raise ArithmeticError("native backend produced non-finite result")
        version = self.lib.sc0_native_version().decode("utf-8", errors="replace")
        return ComputeResult(
            value=value,
            status=ResultStatus.COMPUTED,
            backend=self.name,
            algorithm=f"c_cpp.{op}",
            exact=False,
            tolerance=request.tolerance,
            metadata={"native_version": version, "library": self.library_path},
        )

    @staticmethod
    def _check(status: int, operation: str) -> None:
        if status != 0:
            raise ArithmeticError(f"native operation {operation} failed with status {status}")


def _default_library() -> Path:
    root = Path(__file__).resolve().parents[3]
    system = platform.system()
    if system == "Darwin":
        name = "libsc0native.dylib"
    elif system == "Windows":
        name = "sc0native.dll"
    else:
        name = "libsc0native.so"
    return root / "build" / name


def _work_size(values) -> int:
    total = 0
    stack = list(values)
    while stack:
        item = stack.pop()
        if isinstance(item, (list, tuple)):
            stack.extend(item)
        else:
            total += 1
    return total


def _is_scalar_pair(values) -> bool:
    return len(values) == 2 and all(not isinstance(x, (list, tuple)) for x in values)


def _vector(value) -> list[float]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("expected vector operand")
    return [float(x) for x in value]


def _array(values: Iterable[float]):
    seq = list(values)
    return (ctypes.c_double * len(seq))(*seq)


def _matrix(value) -> tuple[list[float], int, int]:
    if not isinstance(value, (list, tuple)):
        raise TypeError("expected matrix operand")
    rows = len(value)
    if rows == 0:
        return [], 0, 0
    if not all(isinstance(row, (list, tuple)) for row in value):
        raise TypeError("matrix rows must be arrays")
    cols = len(value[0])
    if any(len(row) != cols for row in value):
        raise ValueError("matrix must be rectangular")
    return [float(x) for row in value for x in row], rows, cols


def _finite(value) -> bool:
    if isinstance(value, list):
        return all(_finite(x) for x in value)
    return math.isfinite(float(value))
