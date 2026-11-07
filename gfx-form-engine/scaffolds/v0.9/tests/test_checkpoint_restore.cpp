#include <gfx/runtime/checkpoint_restore.hpp>
#include <cassert>
int main(){
    gfx::RecoveryCheckpoint checkpoint{1,2,3,{4,{5,6,7},8},9,8,10,11,1};
    const auto plan=gfx::plan_restore(checkpoint,2,9,8);
    assert(plan.state==gfx::RestoreState::AuthorizationRequired);
    const gfx::Coordinate expected{5,6,7};
    assert(plan.address.coordinate==expected);
    assert(gfx::plan_restore(checkpoint,2,9,99).state==gfx::RestoreState::Rejected);
}
