#include "sc0_native.h"

#include <cmath>
#include <iostream>
#include <string>

static bool close(double a, double b, double tol = 1e-12) {
    return std::fabs(a - b) <= tol;
}

int main() {
    int failures = 0;
    double out = 0.0;

    if (std::string(sc0_native_version()).find("native-0.8.0") == std::string::npos) ++failures;
    if (sc0_binary_scalar(SC0_MUL, 6.0, 7.0, &out) != SC0_OK || !close(out, 42.0)) ++failures;

    const double v[] = {1.0, 2.0, 3.0, 4.0};
    if (sc0_sum(v, 4, &out) != SC0_OK || !close(out, 10.0)) ++failures;

    const double w[] = {4.0, 3.0, 2.0, 1.0};
    if (sc0_dot(v, w, 4, &out) != SC0_OK || !close(out, 20.0)) ++failures;

    const double a[] = {1, 2, 3, 4, 5, 6};
    const double b[] = {7, 8, 9, 10, 11, 12};
    double m[4] = {};
    if (sc0_matmul(a, 2, 3, b, 3, 2, m) != SC0_OK) ++failures;
    const double expected[] = {58, 64, 139, 154};
    for (int i = 0; i < 4; ++i) if (!close(m[i], expected[i])) ++failures;


    const double la[] = {3, 1, 1, 2};
    if (sc0_det(la, 2, &out) != SC0_OK || !close(out, 5.0)) ++failures;
    const double rhs[] = {9, 8};
    double sol[2] = {};
    if (sc0_solve(la, 2, rhs, 1, sol) != SC0_OK || !close(sol[0], 2.0) || !close(sol[1], 3.0)) ++failures;
    double inv[4] = {};
    if (sc0_inverse(la, 2, inv) != SC0_OK) ++failures;
    const double inv_expected[] = {0.4, -0.2, -0.2, 0.6};
    for (int i = 0; i < 4; ++i) if (!close(inv[i], inv_expected[i])) ++failures;

    if (failures) {
        std::cerr << "native self-test failures=" << failures << "\n";
        return 1;
    }
    std::cout << "native self-test passed: " << sc0_native_version() << "\n";
    return 0;
}
