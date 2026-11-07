#pragma once
#include <cstdint>
#include <limits>

namespace gfx {
using Identity = std::uint64_t;
using Code = std::uint64_t;
using Value = std::uint64_t;
using Mask = std::uint64_t;
using Offset = std::uint64_t;
using Length = std::uint64_t;
using Generation = std::uint64_t;
using TransactionId = std::uint64_t;
using ActivationId = std::uint64_t;
using Sequence = std::uint64_t;

inline constexpr Identity invalid_identity = 0;
inline constexpr Value invalid_value = std::numeric_limits<Value>::max();
}
