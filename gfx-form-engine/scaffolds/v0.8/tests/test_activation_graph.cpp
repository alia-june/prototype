#include <gfx/runtime/activation_graph.hpp>
#include <cassert>
int main(){
    gfx::ActivationGraph g;
    gfx::Activation root{1,10,0,20,0,30,40};
    gfx::Activation child{2,11,1,20,0,30,40};
    gfx::Activation wrong{3,12,99,20,0,30,40};
    assert(g.add(root)); assert(g.add(child)); assert(!g.add(wrong)); assert(g.size()==2);
    assert(g.same_context(1,2)); auto c=g.children(1); assert(c.size()==1 && c[0]==2);
}
