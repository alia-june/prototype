#pragma once
#include <gfx/structures/coordinate.hpp>
#include <cmath>
#include <limits>
namespace gfx {
// Minimal Amanatides/Woo-style state scaffold for exact voxel stepping.
struct DdaState {
    Coordinate voxel{};
    double t_max_x{}, t_max_y{}, t_max_z{};
    double t_delta_x{}, t_delta_y{}, t_delta_z{};
    std::int64_t step_x{}, step_y{}, step_z{};
};
inline Coordinate dda_step(DdaState& s) {
    if (s.t_max_x <= s.t_max_y && s.t_max_x <= s.t_max_z) { s.voxel.x += s.step_x; s.t_max_x += s.t_delta_x; }
    else if (s.t_max_y <= s.t_max_z) { s.voxel.y += s.step_y; s.t_max_y += s.t_delta_y; }
    else { s.voxel.z += s.step_z; s.t_max_z += s.t_delta_z; }
    return s.voxel;
}
}
