#include "sc0_native.h"

#include <cmath>
#include <cstddef>
#include <algorithm>
#include <vector>

extern "C" int sc0_c_kahan_sum(const double *values, size_t n, double *out);
extern "C" int sc0_c_dot(const double *a, const double *b, size_t n, double *out);

namespace {
int finite_result(double value, double *out) {
    if (!out) return SC0_ERR_INVALID;
    if (!std::isfinite(value)) return SC0_ERR_NONFINITE;
    *out = value;
    return SC0_OK;
}
}

extern "C" SC0_API const char *sc0_native_version(void) {
    return "xOSG-0/MATH.SC-0/native-0.8.0";
}

extern "C" SC0_API int sc0_binary_scalar(int op, double a, double b, double *out) {
    if (!out) return SC0_ERR_INVALID;
    switch (op) {
        case SC0_ADD: return finite_result(a + b, out);
        case SC0_SUB: return finite_result(a - b, out);
        case SC0_MUL: return finite_result(a * b, out);
        case SC0_DIV:
            if (b == 0.0) return SC0_ERR_DOMAIN;
            return finite_result(a / b, out);
        case SC0_POW: return finite_result(std::pow(a, b), out);
        default: return SC0_ERR_INVALID;
    }
}

extern "C" SC0_API int sc0_unary_scalar(int op, double a, double *out) {
    if (!out) return SC0_ERR_INVALID;
    switch (op) {
        case SC0_SQRT:
            if (a < 0.0) return SC0_ERR_DOMAIN;
            return finite_result(std::sqrt(a), out);
        case SC0_EXP: return finite_result(std::exp(a), out);
        case SC0_LOG:
            if (a <= 0.0) return SC0_ERR_DOMAIN;
            return finite_result(std::log(a), out);
        case SC0_SIN: return finite_result(std::sin(a), out);
        case SC0_COS: return finite_result(std::cos(a), out);
        case SC0_TAN: return finite_result(std::tan(a), out);
        default: return SC0_ERR_INVALID;
    }
}

extern "C" SC0_API int sc0_sum(const double *values, size_t n, double *out) {
    return sc0_c_kahan_sum(values, n, out);
}

extern "C" SC0_API int sc0_mean(const double *values, size_t n, double *out) {
    if (n == 0) return SC0_ERR_DOMAIN;
    double sum = 0.0;
    int status = sc0_c_kahan_sum(values, n, &sum);
    if (status != SC0_OK) return status;
    return finite_result(sum / static_cast<double>(n), out);
}

extern "C" SC0_API int sc0_norm(const double *values, size_t n, double *out) {
    if (!values || !out) return SC0_ERR_INVALID;
    double sumsq = 0.0;
    double c = 0.0;
    for (size_t i = 0; i < n; ++i) {
        const double term = values[i] * values[i];
        const double y = term - c;
        const double t = sumsq + y;
        c = (t - sumsq) - y;
        sumsq = t;
    }
    if (sumsq < 0.0 || !std::isfinite(sumsq)) return SC0_ERR_NONFINITE;
    return finite_result(std::sqrt(sumsq), out);
}

extern "C" SC0_API int sc0_dot(const double *a, const double *b, size_t n, double *out) {
    return sc0_c_dot(a, b, n, out);
}

extern "C" SC0_API int sc0_vec_binary(int op, const double *a, const double *b, size_t n, double *out) {
    if (!a || !b || !out) return SC0_ERR_INVALID;
    for (size_t i = 0; i < n; ++i) {
        int status = sc0_binary_scalar(op, a[i], b[i], &out[i]);
        if (status != SC0_OK) return status;
    }
    return SC0_OK;
}

extern "C" SC0_API int sc0_matmul(const double *a, size_t a_rows, size_t a_cols,
                                   const double *b, size_t b_rows, size_t b_cols,
                                   double *out) {
    if (!a || !b || !out) return SC0_ERR_INVALID;
    if (a_cols != b_rows) return SC0_ERR_SHAPE;
    for (size_t i = 0; i < a_rows; ++i) {
        for (size_t j = 0; j < b_cols; ++j) {
            double sum = 0.0;
            double c = 0.0;
            for (size_t k = 0; k < a_cols; ++k) {
                const double product = a[i * a_cols + k] * b[k * b_cols + j];
                const double y = product - c;
                const double t = sum + y;
                c = (t - sum) - y;
                sum = t;
            }
            if (!std::isfinite(sum)) return SC0_ERR_NONFINITE;
            out[i * b_cols + j] = sum;
        }
    }
    return SC0_OK;
}


extern "C" SC0_API int sc0_det(const double *a, size_t n, double *out) {
    if (!a || !out || n == 0) return SC0_ERR_INVALID;
    std::vector<double> m(a, a + n * n);
    double det = 1.0;
    int sign = 1;
    for (size_t col = 0; col < n; ++col) {
        size_t pivot = col;
        double best = std::fabs(m[col * n + col]);
        for (size_t row = col + 1; row < n; ++row) {
            const double candidate = std::fabs(m[row * n + col]);
            if (candidate > best) { best = candidate; pivot = row; }
        }
        if (best == 0.0) { *out = 0.0; return SC0_OK; }
        if (pivot != col) {
            for (size_t j = 0; j < n; ++j) std::swap(m[col*n+j], m[pivot*n+j]);
            sign = -sign;
        }
        const double pv = m[col*n+col];
        det *= pv;
        if (!std::isfinite(det)) return SC0_ERR_NONFINITE;
        for (size_t row = col + 1; row < n; ++row) {
            const double factor = m[row*n+col] / pv;
            m[row*n+col] = 0.0;
            for (size_t j = col + 1; j < n; ++j) m[row*n+j] -= factor * m[col*n+j];
        }
    }
    return finite_result(sign < 0 ? -det : det, out);
}

extern "C" SC0_API int sc0_solve(const double *a, size_t n, const double *b, size_t rhs_cols, double *out) {
    if (!a || !b || !out || n == 0 || rhs_cols == 0) return SC0_ERR_INVALID;
    std::vector<double> m(a, a + n * n);
    std::vector<double> x(b, b + n * rhs_cols);
    for (size_t col = 0; col < n; ++col) {
        size_t pivot = col;
        double best = std::fabs(m[col*n+col]);
        for (size_t row = col + 1; row < n; ++row) {
            const double candidate = std::fabs(m[row*n+col]);
            if (candidate > best) { best = candidate; pivot = row; }
        }
        if (best == 0.0) return SC0_ERR_SINGULAR;
        if (pivot != col) {
            for (size_t j = 0; j < n; ++j) std::swap(m[col*n+j], m[pivot*n+j]);
            for (size_t j = 0; j < rhs_cols; ++j) std::swap(x[col*rhs_cols+j], x[pivot*rhs_cols+j]);
        }
        const double pv = m[col*n+col];
        for (size_t row = col + 1; row < n; ++row) {
            const double factor = m[row*n+col] / pv;
            m[row*n+col] = 0.0;
            for (size_t j = col + 1; j < n; ++j) m[row*n+j] -= factor * m[col*n+j];
            for (size_t j = 0; j < rhs_cols; ++j) x[row*rhs_cols+j] -= factor * x[col*rhs_cols+j];
        }
    }
    for (size_t k = 0; k < rhs_cols; ++k) {
        for (size_t ii = n; ii-- > 0;) {
            double acc = x[ii*rhs_cols+k];
            for (size_t j = ii + 1; j < n; ++j) acc -= m[ii*n+j] * out[j*rhs_cols+k];
            const double pv = m[ii*n+ii];
            if (pv == 0.0) return SC0_ERR_SINGULAR;
            const double value = acc / pv;
            if (!std::isfinite(value)) return SC0_ERR_NONFINITE;
            out[ii*rhs_cols+k] = value;
        }
    }
    return SC0_OK;
}

extern "C" SC0_API int sc0_inverse(const double *a, size_t n, double *out) {
    if (!a || !out || n == 0) return SC0_ERR_INVALID;
    std::vector<double> identity(n*n, 0.0);
    for (size_t i = 0; i < n; ++i) identity[i*n+i] = 1.0;
    return sc0_solve(a, n, identity.data(), n, out);
}
