#include <gfx/workloads/json0/parser.hpp>
#include <cassert>
int main(){
 auto d=gfx::json0::parse(R"({"a":[1,2],"b":{"c":3}})",4,2); assert(d.valid()); assert(!d.relations.empty());
 assert(gfx::json0::validate_relationships(d)); assert(gfx::json0::validate_sequence(d));
 auto broken=d; if(!broken.relations.empty()) broken.relations.pop_back(); assert(!gfx::json0::validate_relationships(broken));
}
