#include <gfx/workloads/json0/lexical.hpp>
#include <cassert>
int main(){
    auto r=gfx::json0::build_elr(R"({"a":"{x}","b":[1,2]})");
    assert(r.strings_balanced); assert(r.structure_balanced);
    // braces inside the string must not become structural positions
    std::size_t count=0; for(bool b:r.elr.structural_plane) if(b) ++count;
    assert(count==8); // { : , : [ , ] }
    auto bad=gfx::json0::build_elr("{\"a\": [1,2]");
    assert(!bad.structure_balanced);
}
