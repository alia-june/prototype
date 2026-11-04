#include <math.h>
#include <stddef.h>

/* Pure-C compensated reductions used by the C++ ABI wrapper. */
int sc0_c_kahan_sum(const double *values, size_t n, double *out) {
    if (!values || !out) return 1;
    double sum = 0.0;
    double c = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double y = values[i] - c;
        double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    if (!isfinite(sum)) return 4;
    *out = sum;
    return 0;
}

int sc0_c_dot(const double *a, const double *b, size_t n, double *out) {
    if (!a || !b || !out) return 1;
    double sum = 0.0;
    double c = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double product = a[i] * b[i];
        double y = product - c;
        double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    if (!isfinite(sum)) return 4;
    *out = sum;
    return 0;
}
