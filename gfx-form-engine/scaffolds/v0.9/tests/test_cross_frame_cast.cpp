#include <gfx/structures/cross_frame_cast.hpp>
#include <cassert>
int main(){
    gfx::FrameGraph graph; graph.add({1,100,gfx::FrameRelationKind::TransformsTo,200,50});
    gfx::FrameMappingRegistry mappings;
    gfx::ReindexTransform transform{{0,1,2},{1,1,1},{10,0,0}};
    assert(mappings.insert({50,100,200,transform,9,gfx::ValidationState::Valid}));
    const gfx::Coordinate mapped{11,2,3};
    gfx::Plane<gfx::DirectionIntent> p1(1,200,9);
    gfx::Plane<gfx::PossibilitySet> p2(2,200,9);
    gfx::Plane<gfx::RecoverySet> p3(3,200,9);
    p1.set(mapped,{{1,0,0},{12,2,3},0,1});
    gfx::PossibilitySet allowed; allowed.allowed.push_back({{1,0,0},{12,2,3},0,0}); p2.set(mapped,allowed);
    p3.set(mapped,{});
    const auto result=gfx::resolve_cross_frame_cast(5,{100,{1,2,3},9},200,6,7,8,graph,mappings,p1,p2,p3);
    assert(result.state==gfx::CrossFrameCastState::Resolved);
    assert(result.mapped_address.coordinate==mapped);
    assert(result.resolution.state==gfx::CastResolutionState::Accepted);

    const auto stale=gfx::resolve_cross_frame_cast(5,{100,{1,2,3},8},200,6,7,8,graph,mappings,p1,p2,p3);
    assert(stale.state==gfx::CrossFrameCastState::Rejected);
}
