#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/backing.hpp>

namespace gfx {
struct PlaneDescriptor {
    Identity plane_id{};
    Identity frame_id{};
    Generation generation{};
    BackingBinding backing{};
    Length element_count{};
    Value element_width_bits{};
    Mask validation_mask{};
};
}
