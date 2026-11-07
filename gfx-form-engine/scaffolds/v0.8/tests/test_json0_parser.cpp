#include <gfx/workloads/json0/parser.hpp>
#include <cassert>
int main(){
 using namespace gfx::json0;
 assert(validate_number("0")); assert(validate_number("-12.5e+2")); assert(!validate_number("01")); assert(!validate_number("1."));
 auto d=parse(R"({"a":[1,true,null,{"b":"x\\\"y"}]})",7,3); assert(d.valid()); assert(!d.nodes.empty()); assert(!d.spans.empty()); assert(d.source_id==7 && d.generation==3);
 bool saw_array_order=false; for(auto&s:d.sequence) if(s.semantic_order==SemanticOrder::Required) saw_array_order=true; assert(saw_array_order);
 auto bad=parse(R"({"a":01})"); assert(!bad.valid());
 std::string deep(5000,'['); deep += "0"; deep += std::string(5000,']'); auto dd=parse(deep); assert(dd.valid());

 auto mismatch=parse(R"({])"); assert(!mismatch.valid()); assert(!mismatch.lexical.structure_balanced);
 auto lexical_mismatch=build_elr("{]",1,1); assert(!lexical_mismatch.structure_balanced);
 std::string invalid; invalid.push_back(char(0xC0)); invalid.push_back(char(0xAF)); auto u=parse(invalid); assert(!u.valid());
}
