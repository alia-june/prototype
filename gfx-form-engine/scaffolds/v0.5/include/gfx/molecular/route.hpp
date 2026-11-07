#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <vector>

namespace gfx {
struct RouteStep {
    Identity step_id{};
    CoordinateAddress source{};
    CoordinateAddress destination{};
    Code operation_code{};
    Code state{};
    Identity continuation_id{};
};

struct Route {
    Identity route_id{};
    Identity frame_id{};
    Generation generation{};
    std::vector<RouteStep> steps;

    [[nodiscard]] bool valid_chain() const noexcept {
        for (std::size_t i=0;i<steps.size();++i) {
            const auto& s=steps[i];
            if (s.source.frame_id!=frame_id || s.destination.frame_id!=frame_id) return false;
            if (s.source.generation!=generation || s.destination.generation!=generation) return false;
            if (i+1<steps.size() && !(s.destination == steps[i+1].source)) return false;
        }
        return true;
    }
};
}
