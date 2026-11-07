#include <gfx/runtime/recovery_route.hpp>
#include <cassert>
int main(){
 gfx::CoordinateAddress a{7,{0,0,0},2}, b{7,{0,1,0},2}; gfx::Route route{99,7,2,{{1,a,b,5,0,0}}};
 gfx::RecoveryRouteRegistry registry; assert(registry.insert(route));
 gfx::CastResolution r; r.state=gfx::CastResolutionState::RecoveryRequired; r.recovery_candidate=gfx::RecoveryOption{3,{0,1,0},5,1,10,99};
 auto selected=registry.select(r); assert(selected.available); assert(selected.route && selected.route->route_id==99);
 gfx::CastResolution absent; auto none=registry.select(absent); assert(!none.available);
}
