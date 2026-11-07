#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/molecular/recursion.hpp>
#include <gfx/runtime/recursion_governor.hpp>
#include <unordered_map>

namespace gfx {

struct RecursionObservation {
    Identity recursion_id{};
    Identity state_token{};       // regime-defined state fingerprint, not native stack address
    Value progress_measure{};     // regime-defined monotonic/forward-progress evidence
    Value resource_consumed{};
    Value resource_budget{};
    bool reference_valid{true};
    bool transition_valid{true};
    bool continuation_valid{true};
    bool sentinels_valid{true};
};

struct RecursionPolicy {
    Value permitted_equal_progress_observations{1};
    Value permitted_state_revisits{1};
};

class RecursionMonitor {
public:
    explicit RecursionMonitor(RecursionPolicy policy = {}) : policy_(policy) {}

    RecursionGovernanceResult observe(const RecursionObservation& o) {
        RecursionInvariantSet i;
        i.reference_valid = o.reference_valid;
        i.transition_valid = o.transition_valid;
        i.continuation_valid = o.continuation_valid;
        i.sentinels_valid = o.sentinels_valid;
        i.resource_valid = o.resource_budget == 0 || o.resource_consumed <= o.resource_budget;

        auto& state = states_[o.recursion_id];
        if (state.seen) {
            if (o.progress_measure < state.last_progress) i.progress_valid = false;
            else if (o.progress_measure == state.last_progress) {
                ++state.equal_progress_count;
                i.progress_valid = state.equal_progress_count <= policy_.permitted_equal_progress_observations;
            } else {
                state.equal_progress_count = 0;
            }
        }
        auto& visits = state.visits[o.state_token];
        ++visits;
        i.cycle_policy_valid = visits <= policy_.permitted_state_revisits + 1;
        state.last_progress = o.progress_measure;
        state.seen = true;
        return evaluate_recursion(i);
    }

    void clear(Identity recursion_id) { states_.erase(recursion_id); }

private:
    struct State {
        bool seen{false};
        Value last_progress{};
        Value equal_progress_count{};
        std::unordered_map<Identity,Value> visits;
    };
    RecursionPolicy policy_;
    std::unordered_map<Identity,State> states_;
};
}
