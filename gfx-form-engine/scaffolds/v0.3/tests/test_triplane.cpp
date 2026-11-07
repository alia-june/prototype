#include <gfx/structures/aligned_planes.hpp>
#include <gfx/runtime/cast_trace.hpp>
#include <cassert>
int main(){
 gfx::Plane<gfx::DirectionIntent> p1(1,100,9); gfx::Plane<gfx::PossibilitySet> p2(2,100,9); gfx::Plane<gfx::RecoverySet> p3(3,100,9); gfx::Coordinate c{4,5,6};
 p1.set(c,{{1,0,0},{5,5,6},0,1}); gfx::PossibilitySet ps; ps.allowed.push_back({{1,0,0},{5,5,6},0,0}); p2.set(c,ps); gfx::RecoverySet rs; rs.options.push_back({1,{4,5,6},2,1,1}); p3.set(c,rs);
 auto ar=gfx::read_aligned(22,{100,c,9},44,55,1,p1,p2,p3); auto r=gfx::resolve_aligned(ar); assert(r.state==gfx::CastResolutionState::Accepted); auto t=gfx::make_cast_trace(ar.bundle,r); assert(t.plane1_present&&t.plane2_present&&t.plane3_present);
 gfx::Plane<gfx::RecoverySet> stale(4,100,8); stale.set(c,rs); auto ar2=gfx::read_aligned(23,{100,c,9},44,55,1,p1,p2,stale); assert(gfx::resolve_aligned(ar2).state==gfx::CastResolutionState::InvalidAlignment);
}
