#include <gfx/workloads/json0/mutation.hpp>
#include <cassert>
int main(){
    const auto original=gfx::json0::parse("{\"a\":1,\"b\":2}",5,1);
    assert(original.valid());
    gfx::json0::SourceMutationPlan plan{1,5,1,2,{{5,1,"99"}}};
    assert(gfx::json0::validate_mutation_plan(original,plan)==gfx::json0::MutationValidation::Valid);
    auto mutated=gfx::json0::apply_mutation(original,plan); assert(mutated && mutated->valid());
    assert(mutated->generation==2 && mutated->source_text=="{\"a\":99,\"b\":2}");
    assert(original.source_text=="{\"a\":1,\"b\":2}");

    auto overlap=plan; overlap.edits={{5,2,"x"},{6,1,"y"}};
    assert(gfx::json0::validate_mutation_plan(original,overlap)==gfx::json0::MutationValidation::Overlap);
    auto stale=plan; stale.expected_generation=9;
    assert(gfx::json0::validate_mutation_plan(original,stale)==gfx::json0::MutationValidation::StaleGeneration);

    gfx::Elr elr; elr.elr_id=20; elr.source_id=5; elr.source_generation=1; elr.generation=8;
    auto rebuild=gfx::json0::plan_elr_rebuild(30,elr,plan); assert(rebuild && rebuild->full_rebuild_required);
}
