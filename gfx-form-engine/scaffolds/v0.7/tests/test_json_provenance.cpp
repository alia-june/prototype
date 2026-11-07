#include <gfx/workloads/json0/parser.hpp>
#include <cassert>
int main(){
    auto d=gfx::json0::parse(R"({"a":[1,true]})",44,9);
    assert(d.valid()); assert(!d.references.empty()); assert(!d.provenance.empty());
    const auto source_ref=d.references.front();
    assert(source_ref.target_id==44); assert(source_ref.expected_generation==9);
    for(const auto& p:d.provenance) { assert(p.generation==9); assert(p.source_reference_id==source_ref.reference_id); }
}
