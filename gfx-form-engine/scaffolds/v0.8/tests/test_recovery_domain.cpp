#include <gfx/runtime/recovery_domain.hpp>
#include <cassert>
int main(){
    gfx::RecoveryDomainRegistry r;
    gfx::RecoveryDomain d; d.domain_id=1; d.generation=5; d.activations={10,11}; d.route_ids={20};
    assert(r.add(d)); assert(r.get(1)->contains_activation(11));
    assert(r.transition(1,gfx::RecoveryDomainState::Active,gfx::RecoveryDomainState::Faulted));
    assert(!r.transition(1,gfx::RecoveryDomainState::Active,gfx::RecoveryDomainState::Recovering));
    assert(r.transition(1,gfx::RecoveryDomainState::Faulted,gfx::RecoveryDomainState::Recovering));
}
