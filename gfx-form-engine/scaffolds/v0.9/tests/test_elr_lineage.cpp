#include <gfx/structures/elr_lineage.hpp>
#include <cassert>
int main(){
    gfx::ElrLineage lineage;
    assert(lineage.append({1,9,gfx::ElrStage::Source,1,0,100,1}));
    assert(lineage.append({2,9,gfx::ElrStage::Classify,2,1,101,1}));
    assert(lineage.append({3,9,gfx::ElrStage::String,3,2,102,1}));
    assert(lineage.valid());
    assert(!lineage.append({4,9,gfx::ElrStage::Structure,4,1,103,1}));
}
