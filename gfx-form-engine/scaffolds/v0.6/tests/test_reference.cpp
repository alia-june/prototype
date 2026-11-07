#include <gfx/molecular/reference.hpp>
#include <cassert>
int main(){
    gfx::Reference r; r.target_id=9; r.expected_generation=4; r.authority_mask=0b11;
    gfx::ReferenceTargetState t{9,4,0b11,true};
    assert(gfx::validate_reference(r,t)==gfx::ValidationState::Valid);
    t.generation=5;
    assert(gfx::validate_reference(r,t)==gfx::ValidationState::Invalid);
}
