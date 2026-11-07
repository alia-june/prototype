#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
enum class Sentinel : Mask {
    None=0,
    BoundsValid=1ull<<0,
    GenerationValid=1ull<<1,
    ReferenceValid=1ull<<2,
    ProgressValid=1ull<<3,
    SequenceValid=1ull<<4,
    StructureValid=1ull<<5,
    OutputValid=1ull<<6
};
constexpr Mask bit(Sentinel s) noexcept { return static_cast<Mask>(s); }
struct SentinelReport { Mask passed{}; Mask failed{}; [[nodiscard]] bool ok() const noexcept { return failed==0; } };
}
