#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <vector>

namespace gfx {
template<class T>
struct FragmentRequirement {
    Coordinate local_coordinate{};
    T expected{};
    Mask required_flags{};
};

template<class T>
struct FormFragment {
    Identity fragment_id{};
    Identity local_frame_id{};
    Generation generation{};
    std::vector<FragmentRequirement<T>> requirements;
};
}
