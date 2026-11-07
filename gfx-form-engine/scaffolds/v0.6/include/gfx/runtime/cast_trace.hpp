#pragma once
#include <gfx/structures/cast.hpp>
#include <gfx/runtime/trace.hpp>
namespace gfx {
struct CastTraceRecord {
    Identity cast_id{}; CoordinateAddress address{}; TransactionId transaction_id{}; ActivationId activation_id{};
    bool plane1_present{}; bool plane2_present{}; bool plane3_present{}; CastResolutionState resolution{CastResolutionState::MissingData}; Coordinate selected_target{}; Mask sentinels{};
};
inline CastTraceRecord make_cast_trace(const CastBundle& b, const CastResolution& r) {
    return {b.cast_id,b.address,b.transaction_id,b.activation_id,b.plane1.has_value(),b.plane2.has_value(),b.plane3.has_value(),r.state,r.selected_target,r.sentinel_mask};
}
}
