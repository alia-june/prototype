#pragma once
#include <gfx/molecular/recursion.hpp>
#include <optional>
#include <unordered_map>
#include <vector>

namespace gfx {
class ActivationGraph {
public:
    bool add(Activation activation) {
        if (!activation.activation_id || activations_.count(activation.activation_id)) return false;
        if (activation.parent_activation_id && !activations_.count(activation.parent_activation_id)) return false;
        activations_.emplace(activation.activation_id, activation);
        if (activation.parent_activation_id) children_[activation.parent_activation_id].push_back(activation.activation_id);
        return true;
    }
    const Activation* get(ActivationId id) const noexcept {
        const auto it=activations_.find(id); return it==activations_.end()?nullptr:&it->second;
    }
    std::vector<ActivationId> children(ActivationId id) const {
        const auto it=children_.find(id); return it==children_.end()?std::vector<ActivationId>{}:it->second;
    }
    bool same_context(ActivationId parent, ActivationId child) const noexcept {
        const auto* p=get(parent); const auto* c=get(child);
        return p && c && c->parent_activation_id==parent && p->transaction_id==c->transaction_id && p->generation==c->generation;
    }
    [[nodiscard]] std::size_t size() const noexcept { return activations_.size(); }
private:
    std::unordered_map<ActivationId,Activation> activations_;
    std::unordered_map<ActivationId,std::vector<ActivationId>> children_;
};
}
