#include <gfx/workloads/json0/parser.hpp>
#include <cassert>
int main(){
    using namespace gfx::json0;
    auto good=parse(R"({"music":"\uD834\uDD1E"})"); assert(good.valid());
    auto high=parse(R"({"bad":"\uD834x"})"); assert(!high.valid());
    auto low=parse(R"({"bad":"\uDD1E"})"); assert(!low.valid());
    auto d=parse(R"({"alpha":[1,2]})"); assert(d.valid());
    bool member_span=false,key_rel=false,value_rel=false;
    for(const auto& node:d.nodes) if(node.node_type==NodeType::Member){ member_span=node.source_span_id!=0; for(const auto& r:d.relations){ if(r.source_id!=node.node_id) continue; key_rel|=r.relation_code==static_cast<gfx::Code>(JsonRelationCode::MemberKey); value_rel|=r.relation_code==static_cast<gfx::Code>(JsonRelationCode::MemberValue); }}
    assert(member_span&&key_rel&&value_rel);
}
