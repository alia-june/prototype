#pragma once
#include <gfx/atomic/types.hpp>
#include <algorithm>
#include <unordered_map>
#include <vector>

namespace gfx {
enum class RecoveryDomainState : Code { Active=0, Quiesced=1, Faulted=2, Recovering=3, Quarantined=4, Retired=5 };
struct RecoveryDomain {
    Identity domain_id{};
    Generation generation{};
    RecoveryDomainState state{RecoveryDomainState::Active};
    std::vector<ActivationId> activations;
    std::vector<Identity> route_ids;
    std::vector<Identity> backing_ids;
    [[nodiscard]] bool contains_activation(ActivationId id) const noexcept { return std::find(activations.begin(),activations.end(),id)!=activations.end(); }
};
class RecoveryDomainRegistry {
public:
    bool add(RecoveryDomain d) { return d.domain_id && domains_.emplace(d.domain_id,std::move(d)).second; }
    RecoveryDomain* get(Identity id) noexcept { auto it=domains_.find(id); return it==domains_.end()?nullptr:&it->second; }
    const RecoveryDomain* get(Identity id) const noexcept { auto it=domains_.find(id); return it==domains_.end()?nullptr:&it->second; }
    bool transition(Identity id, RecoveryDomainState expected, RecoveryDomainState next) noexcept {
        auto* d=get(id); if(!d || d->state!=expected) return false; d->state=next; return true;
    }
private:
    std::unordered_map<Identity,RecoveryDomain> domains_;
};
}
