#pragma once
#include <gfx/molecular/route.hpp>
#include <gfx/structures/cast.hpp>
#include <gfx/structures/backing_pool.hpp>
#include <optional>

namespace gfx {
struct RecoveryRouteSelection {
    RecoveryOption option{};
    const Route* route{};
    bool available{false};
};

class RecoveryRouteRegistry {
public:
    bool insert(Route route) { return routes_.insert(route.route_id, std::move(route)); }
    RecoveryRouteSelection select(const CastResolution& resolution) const {
        if (!resolution.recovery_candidate) return {};
        RecoveryRouteSelection out; out.option=*resolution.recovery_candidate;
        if (out.option.route_id==0) return out;
        out.route=routes_.find(out.option.route_id);
        out.available=out.route && out.route->valid_chain();
        return out;
    }
private:
    HomogeneousBackingPool<Route> routes_;
};
}
