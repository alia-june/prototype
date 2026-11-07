#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/molecular/reference.hpp>
#include <optional>
#include <unordered_set>

namespace gfx {
struct Coordinate;

struct Activation {
    ActivationId activation_id{};
    Identity subject_reference_id{};
    ActivationId parent_activation_id{};
    Identity frame_id{};
    Code state{};
    TransactionId transaction_id{};
    Generation generation{};
};

struct Continuation {
    Identity continuation_id{};
    ActivationId caller_activation_id{};
    Identity return_reference_id{};
    Identity resume_frame_id{};
    std::uint64_t resume_x{}, resume_y{}, resume_z{};
    Code resume_state{};
    Identity result_destination_id{};
    Generation generation{};
};

struct Progress {
    Identity progress_id{};
    Identity recursion_id{};
    Value progress_measure{};
    Value previous_measure{};
    Code progress_state{};
    Identity evidence_reference_id{};
};

struct Recursion {
    Identity recursion_id{};
    Identity recursive_reference_id{};
    ActivationId activation_id{};
    Identity continuation_id{};
    Identity progress_id{};
    Identity recovery_binding_id{};
    Value observed_depth{}; // diagnostic, not a universal bound
    Code state{};
};

struct RecursionInvariantSet {
    bool reference_valid{true};
    bool transition_valid{true};
    bool progress_valid{true};
    bool resource_valid{true};
    bool continuation_valid{true};
    bool cycle_policy_valid{true};
    bool sentinels_valid{true};
    [[nodiscard]] bool permits_continue() const noexcept {
        return reference_valid && transition_valid && progress_valid && resource_valid &&
               continuation_valid && cycle_policy_valid && sentinels_valid;
    }
};

enum class RecursionDisposition : Code { Continue=0, EnterRecoveryPlane=1 };
RecursionDisposition govern_recursion(const RecursionInvariantSet& invariants) noexcept;
}
