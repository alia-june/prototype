#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build"
INCLUDE="$ROOT/native/include"
mkdir -p "$BUILD"

CC="${CC:-gcc}"
CXX="${CXX:-g++}"
CFLAGS="${CFLAGS:--O3 -fPIC -Wall -Wextra -Werror}"
CXXFLAGS="${CXXFLAGS:--O3 -fPIC -Wall -Wextra -Werror -std=c++17}"

case "$(uname -s)" in
  Darwin*) LIB="$BUILD/libsc0native.dylib"; SHARED_FLAGS="-dynamiclib" ;;
  Linux*)  LIB="$BUILD/libsc0native.so"; SHARED_FLAGS="-shared" ;;
  *) echo "Unsupported build host for this script: $(uname -s)" >&2; exit 2 ;;
esac

$CC $CFLAGS -I"$INCLUDE" -c "$ROOT/native/src/sc0_reduce.c" -o "$BUILD/sc0_reduce.o"
$CXX $CXXFLAGS -DSC0_NATIVE_BUILD -I"$INCLUDE" -c "$ROOT/native/src/sc0_native.cpp" -o "$BUILD/sc0_native.o"
$CXX $SHARED_FLAGS "$BUILD/sc0_reduce.o" "$BUILD/sc0_native.o" -o "$LIB"
$CXX -O2 -Wall -Wextra -Werror -std=c++17 -I"$INCLUDE" "$ROOT/native/tests/native_selftest.cpp" \
  -L"$BUILD" -lsc0native -Wl,-rpath,"$BUILD" -o "$BUILD/native_selftest"
"$BUILD/native_selftest"
printf '%s\n' "$LIB"
