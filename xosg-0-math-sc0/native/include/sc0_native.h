#ifndef XOSG_SC0_NATIVE_H
#define XOSG_SC0_NATIVE_H

#include <stddef.h>

#ifdef _WIN32
  #ifdef SC0_NATIVE_BUILD
    #define SC0_API __declspec(dllexport)
  #else
    #define SC0_API __declspec(dllimport)
  #endif
#else
  #define SC0_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

enum sc0_status {
    SC0_OK = 0,
    SC0_ERR_INVALID = 1,
    SC0_ERR_DOMAIN = 2,
    SC0_ERR_SHAPE = 3,
    SC0_ERR_NONFINITE = 4,
    SC0_ERR_SINGULAR = 5
};

enum sc0_binary_op {
    SC0_ADD = 1,
    SC0_SUB = 2,
    SC0_MUL = 3,
    SC0_DIV = 4,
    SC0_POW = 5
};

enum sc0_unary_op {
    SC0_SQRT = 1,
    SC0_EXP = 2,
    SC0_LOG = 3,
    SC0_SIN = 4,
    SC0_COS = 5,
    SC0_TAN = 6
};

SC0_API const char *sc0_native_version(void);
SC0_API int sc0_binary_scalar(int op, double a, double b, double *out);
SC0_API int sc0_unary_scalar(int op, double a, double *out);
SC0_API int sc0_sum(const double *values, size_t n, double *out);
SC0_API int sc0_mean(const double *values, size_t n, double *out);
SC0_API int sc0_norm(const double *values, size_t n, double *out);
SC0_API int sc0_dot(const double *a, const double *b, size_t n, double *out);
SC0_API int sc0_vec_binary(int op, const double *a, const double *b, size_t n, double *out);
SC0_API int sc0_matmul(const double *a, size_t a_rows, size_t a_cols,
                       const double *b, size_t b_rows, size_t b_cols,
                       double *out);
SC0_API int sc0_det(const double *a, size_t n, double *out);
SC0_API int sc0_solve(const double *a, size_t n, const double *b, size_t rhs_cols, double *out);
SC0_API int sc0_inverse(const double *a, size_t n, double *out);

#ifdef __cplusplus
}
#endif

#endif
