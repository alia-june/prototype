#include <gfx/molecular/composition.hpp>
#include <cassert>
int main(){
    gfx::Composition c{1,42,{10,11,12},{20,21}};
    gfx::Decomposition d{2,42,{12,10,11},{21,20}};
    auto ok=gfx::validate_round_trip(c,d); assert(ok.equivalent());
    d.component_reference_ids.pop_back(); assert(!gfx::validate_round_trip(c,d).equivalent());
}
