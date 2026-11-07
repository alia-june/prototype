#include <gfx/structures/frame_path.hpp>
#include <cassert>
int main(){
    gfx::FrameGraph graph; graph.add({1,10,gfx::FrameRelationKind::TransformsTo,20,100}); graph.add({2,20,gfx::FrameRelationKind::TransformsTo,30,101});
    auto path=graph.path(10,30); assert(path && path->size()==2);
    gfx::FrameMappingRegistry mappings;
    gfx::ReindexTransform a{{0,1,2},{1,1,1},{1,0,0}}; gfx::ReindexTransform b{{1,0,2},{1,1,1},{0,2,0}};
    assert(mappings.insert({100,10,20,a,5,gfx::ValidationState::Valid}));
    assert(mappings.insert({101,20,30,b,5,gfx::ValidationState::Valid}));
    auto mapped=gfx::map_frame_path({10,{3,4,5},5},*path,mappings); assert(mapped && mapped->frame_id==30);
    const gfx::Coordinate expected{4,6,5}; assert(mapped->coordinate==expected);
}
