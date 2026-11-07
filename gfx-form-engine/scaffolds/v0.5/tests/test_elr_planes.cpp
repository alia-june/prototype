#include <gfx/workloads/json0/lexical.hpp>
#include <cassert>
int main(){
 auto r=gfx::json0::build_elr(R"({"a":"{x}"})",9,4); assert(r.elr.plane_descriptors.size()==7);
 for(const auto& p:r.elr.plane_descriptors){ assert(p.source_generation==4); assert(p.generation==4); assert(p.element_count==11); }
 assert(r.structure.size()==3); // { : }
}
