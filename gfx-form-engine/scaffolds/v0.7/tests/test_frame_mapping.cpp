#include <gfx/structures/frame_mapping.hpp>
#include <cassert>
int main(){
    gfx::ReindexTransform t{{2,0,1},{1,-1,1},{10,20,30}};
    assert(t.valid());
    gfx::Coordinate c{3,4,5}; auto m=t.apply(c); const gfx::Coordinate expected{15,17,34}; assert(m==expected);
    auto back=t.inverse(m); assert(back && *back==c);
    gfx::FrameTransformBinding b{77,100,200,t,9,gfx::ValidationState::Valid};
    auto mapped=gfx::map_address({100,c,9},b); assert(mapped); assert(mapped->frame_id==200); assert(mapped->coordinate==m);
    gfx::SemanticProjection p{88,100,300,{1,2},{3},gfx::ProjectionLoss::Declared,900,gfx::ValidationState::Valid};
    assert(p.loss==gfx::ProjectionLoss::Declared && p.validation_state==gfx::ValidationState::Valid);
}
