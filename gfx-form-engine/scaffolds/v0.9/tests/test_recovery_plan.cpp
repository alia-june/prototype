#include <gfx/runtime/recovery_plan.hpp>
#include <cassert>
int main(){
    const gfx::CoordinateAddress start{10,{1,2,3},7};
    const gfx::CoordinateAddress finish{10,{2,2,3},7};
    gfx::Route route{30,10,7,{{1,start,finish,9,0,0}}};
    gfx::RecoveryCheckpoint checkpoint{40,50,60,start,70,7,100,3,1};
    gfx::RecoveryDomain domain{80,7,gfx::RecoveryDomainState::Faulted,{60},{30},{}};
    auto plan=gfx::validate_recovery_plan(90,checkpoint,route,domain,50,70,7);
    assert(plan.state==gfx::RecoveryPlanState::AuthorizationRequired);
    gfx::RecoveryAuthorization auth{99,70,30,7,1,true};
    plan=gfx::authorize_recovery_plan(plan,auth);
    assert(plan.state==gfx::RecoveryPlanState::Authorized);

    auto active=domain; active.state=gfx::RecoveryDomainState::Active;
    auto rejected=gfx::validate_recovery_plan(91,checkpoint,route,active,50,70,7);
    assert(rejected.state==gfx::RecoveryPlanState::Rejected);
    assert(rejected.failure==gfx::RecoveryPlanFailure::InvalidDomain);

    auto wrong=domain; wrong.route_ids={31};
    rejected=gfx::validate_recovery_plan(92,checkpoint,route,wrong,50,70,7);
    assert(rejected.failure==gfx::RecoveryPlanFailure::RouteNotInDomain);
}
