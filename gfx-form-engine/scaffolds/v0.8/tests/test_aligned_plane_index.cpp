#include <gfx/structures/aligned_plane_index.hpp>
#include <cassert>
int main(){
    gfx::Plane<gfx::DirectionIntent> p1(1,7,3); gfx::Plane<gfx::PossibilitySet> p2(2,7,3); gfx::Plane<gfx::RecoverySet> p3(3,7,3);
    const gfx::Coordinate c{1,2,3}; const gfx::Direction d{1,0,0}; const gfx::Coordinate target{2,2,3};
    p1.set(c,{d,target,1,1}); p2.set(c,{{{d,target,1,1}},1}); p3.set(c,{{{9,{0,0,0},2,1,1,5}}});
    gfx::AlignedPlaneIndex index(7,3,42); assert(index.build(p1,p2,p3,{c}));
    const auto* e=index.get(c); assert(e && e->direction && e->possibilities && e->recovery);
    assert(index.validation_epoch()==42);
}
