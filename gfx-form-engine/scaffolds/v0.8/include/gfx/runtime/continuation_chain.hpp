#pragma once
#include <gfx/molecular/recursion.hpp>
#include <optional>
#include <unordered_set>
#include <vector>

namespace gfx {
struct ContinuationChain {
    Identity chain_id{};
    Identity recursion_id{};
    Generation generation{};
    std::vector<Continuation> entries;

    bool push(Continuation c) {
        if (!c.continuation_id || c.generation!=generation) return false;
        for (const auto& e:entries) if (e.continuation_id==c.continuation_id) return false;
        entries.push_back(c); return true;
    }
    std::optional<Continuation> pop() {
        if (entries.empty()) return std::nullopt;
        auto c=entries.back(); entries.pop_back(); return c;
    }
    [[nodiscard]] const Continuation* top() const noexcept { return entries.empty()?nullptr:&entries.back(); }
    [[nodiscard]] bool valid() const noexcept {
        std::unordered_set<Identity> ids;
        for (const auto& c:entries) if (!c.continuation_id || c.generation!=generation || !ids.insert(c.continuation_id).second) return false;
        return true;
    }
};
}
