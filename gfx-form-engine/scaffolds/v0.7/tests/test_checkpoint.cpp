#include <gfx/runtime/checkpoint.hpp>
#include <cassert>
int main(){
    gfx::CheckpointStore store;
    store.add({1,9,20,{3,{1,2,3},4},30,4,10,7,0});
    store.add({2,9,21,{3,{2,2,3},4},31,4,11,8,1});
    auto cp=store.latest_valid(9,4); assert(cp && cp->checkpoint_id==2 && cp->progress_measure==11);
    assert(!store.latest_valid(9,5));
}
