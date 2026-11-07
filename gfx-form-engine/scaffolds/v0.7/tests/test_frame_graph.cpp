#include <gfx/structures/frame_relation.hpp>
#include <cassert>
int main(){
 gfx::FrameGraph g; g.add({1,10,gfx::FrameRelationKind::TransformsTo,20,100}); g.add({2,20,gfx::FrameRelationKind::AlignsWith,30,101});
 auto p=g.path(10,30); assert(p); assert(p->size()==2); assert((*p)[0].source_frame_id==10); assert((*p)[1].target_frame_id==30);
 assert(!g.path(30,10)); auto same=g.path(10,10); assert(same&&same->empty());
}
