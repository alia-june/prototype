#include <gfx/runtime/breadcrumb.hpp>
#include <gfx/runtime/heartbeat.hpp>
#include <cassert>
int main(){
    gfx::BreadcrumbRing r(3);
    for(gfx::Sequence i=1;i<=4;++i) assert(r.push({i,100+i,1,2,{static_cast<std::int64_t>(i),0,0},7,9,gfx::ExecutionPhase::Effect,0}));
    auto s=r.snapshot(); assert(s.size()==3); assert(s[0].sequence==2 && s[2].sequence==4);
    gfx::SemanticHeartbeat h{1,2,7,20,19,9,0,0,4}; assert(h.sane());
    h.last_completed_transaction=21; assert(!h.sane());
}
