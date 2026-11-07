#include <gfx/runtime/recursion_monitor.hpp>
#include <cassert>
int main(){
    gfx::RecursionMonitor monitor({1,1});
    // Arbitrary observed depth is irrelevant: progress permits continuation.
    auto a=monitor.observe({1,10,1,1,100,true,true,true,true});
    assert(a.disposition==gfx::RecursionDisposition::Continue);
    auto b=monitor.observe({1,11,2,2,100,true,true,true,true});
    assert(b.disposition==gfx::RecursionDisposition::Continue);
    // Stalled progress is tolerated once, then diverted to recovery.
    auto c=monitor.observe({1,12,2,3,100,true,true,true,true});
    assert(c.disposition==gfx::RecursionDisposition::Continue);
    auto d=monitor.observe({1,13,2,4,100,true,true,true,true});
    assert(d.disposition==gfx::RecursionDisposition::EnterRecoveryPlane);
    assert(d.reason==gfx::RecursionRecoveryReason::Progress);
    monitor.clear(1);
    auto e=monitor.observe({1,10,1,101,100,true,true,true,true});
    assert(e.reason==gfx::RecursionRecoveryReason::Resource);
}
