#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <vector>
#include <optional>

namespace gfx {
struct RecoveryCheckpoint {
    Identity checkpoint_id{};
    Identity recursion_id{};
    ActivationId activation_id{};
    CoordinateAddress address{};
    TransactionId transaction_id{};
    Generation generation{};
    Value progress_measure{};
    Code state{};
    Mask validation_mask{};
};
class CheckpointStore {
public:
    void add(RecoveryCheckpoint checkpoint) { checkpoints_.push_back(std::move(checkpoint)); }
    std::optional<RecoveryCheckpoint> latest_valid(Identity recursion_id, Generation generation) const {
        for(auto it=checkpoints_.rbegin();it!=checkpoints_.rend();++it)
            if(it->recursion_id==recursion_id && it->generation==generation && it->validation_mask!=0) return *it;
        return std::nullopt;
    }
    const std::vector<RecoveryCheckpoint>& all() const noexcept { return checkpoints_; }
private:
    std::vector<RecoveryCheckpoint> checkpoints_;
};
}
