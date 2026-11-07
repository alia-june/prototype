#include <gfx/runtime/route_commit.hpp>
#include <cassert>
int main(){
    gfx::CoordinateAddress a{7,{0,0,0},2}, b{7,{1,0,0},2};
    gfx::Route route{99,7,2,{{1,a,b,5,0,0}}}; gfx::TransactionLedger ledger;
    auto prep=gfx::prepare_route(ledger,10,55,route,1); assert(prep.state==gfx::RouteCommitState::Prepared);
    auto committed=gfx::commit_route(ledger,10,55,route,1); assert(committed.state==gfx::RouteCommitState::Committed); assert(ledger.has_commit(10,2));
    gfx::TransactionLedger recovery_ledger; gfx::prepare_route(recovery_ledger,11,55,route,1);
    gfx::RecoveryAuthorization denied{0,11,99,2,0,false};
    assert(gfx::commit_recovery_route(recovery_ledger,11,55,route,1,denied).state==gfx::RouteCommitState::RecoveryAuthorizationRequired);
    gfx::RecoveryAuthorization allowed{800,11,99,2,0x1,true};
    assert(gfx::commit_recovery_route(recovery_ledger,11,55,route,1,allowed).state==gfx::RouteCommitState::Committed);
}
