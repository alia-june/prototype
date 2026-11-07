#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <gfx/structures/backing.hpp>
namespace gfx {
struct Voxel {
    Identity voxel_id{};
    CoordinateAddress address{};
    Code class_code{};
    Code state_code{};
    BackingBinding backing{};
};
}
