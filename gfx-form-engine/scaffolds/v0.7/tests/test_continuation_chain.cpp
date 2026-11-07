#include <gfx/runtime/continuation_chain.hpp>
#include <cassert>
int main(){
    gfx::ContinuationChain c{1,2,7,{}};
    gfx::Continuation a{10,1,100,3,4,5,6,9,200,7};
    gfx::Continuation b{11,2,101,3,7,8,9,10,201,7};
    gfx::Continuation stale{12,3,102,3,0,0,0,0,202,8};
    assert(c.push(a)); assert(c.push(b)); assert(!c.push(stale)); assert(c.valid());
    auto p=c.pop(); assert(p && p->continuation_id==11); assert(c.top() && c.top()->continuation_id==10);
}
