#pragma once
#include <gfx/runtime/checkpoint.hpp>
#include <optional>

namespace gfx {
enum class RestoreState : Code { Rejected=0, Candidate=1, AuthorizationRequired=2 };
struct RestorePlan {
    RestoreState state{RestoreState::Rejected};
    Identity checkpoint_id{};
    Identity recursion_id{};
    ActivationId activation_id{};
    CoordinateAddress address{};
    TransactionId transaction_id{};
    Generation generation{};
    Code restored_state{};
};

inline RestorePlan plan_restore(const RecoveryCheckpoint& checkpoint, Identity recursion_id,
                                TransactionId transaction_id, Generation generation) noexcept {
    if (!checkpoint.checkpoint_id || !checkpoint.validation_mask || checkpoint.recursion_id != recursion_id ||
        checkpoint.transaction_id != transaction_id || checkpoint.generation != generation)
        return {};
    return {RestoreState::AuthorizationRequired, checkpoint.checkpoint_id, checkpoint.recursion_id,
            checkpoint.activation_id, checkpoint.address, checkpoint.transaction_id, checkpoint.generation,
            checkpoint.state};
}
}
