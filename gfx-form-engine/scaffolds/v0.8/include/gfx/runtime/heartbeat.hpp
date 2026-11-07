#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
struct SemanticHeartbeat {
    Identity worker_instance_id{};
    Value orchestrator_epoch{};
    Generation active_generation{};
    TransactionId last_received_transaction{};
    TransactionId last_completed_transaction{};
    Code current_opcode{};
    Code queue_state{};
    Mask sentinel_summary{};
    Value validation_epoch{};
    [[nodiscard]] bool sane() const noexcept {
        return worker_instance_id!=0 && active_generation!=0 && last_completed_transaction<=last_received_transaction;
    }
};
}
