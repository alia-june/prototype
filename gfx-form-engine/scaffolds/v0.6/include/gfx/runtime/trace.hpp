#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
namespace gfx {
struct TraceRecord {
    Sequence trace_sequence{};
    TransactionId transaction_id{};
    ActivationId activation_id{};
    Identity frame_id{};
    Coordinate coordinate{};
    Identity matrix_id{};
    Identity cell_id{};
    Code opcode{};
    Code transfer_type{};
    Code state_before{};
    Code state_after{};
    Mask sentinel_summary{};
    Identity continuation_id{};
};
}
