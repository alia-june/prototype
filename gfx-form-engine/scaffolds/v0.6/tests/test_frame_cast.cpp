#include <gfx/structures/cast.hpp>
#include <cassert>
int main(){
    gfx::CastBundle b; b.address={1,{2,3,4},1};
    gfx::DirectionIntent d{{1,0,0},{3,3,4},0,1}; b.plane1=d;
    gfx::PossibilitySet ps; ps.allowed.push_back({{1,0,0},{3,3,4},0,0}); b.plane2=ps;
    b.plane3=gfx::RecoverySet{};
    auto r=gfx::resolve_cast(b); assert(r.state==gfx::CastResolutionState::Accepted); const gfx::Coordinate expected{3,3,4}; assert(r.selected_target==expected);
}
