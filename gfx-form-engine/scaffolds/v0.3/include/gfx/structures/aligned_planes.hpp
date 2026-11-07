#pragma once
#include <gfx/structures/cast.hpp>
namespace gfx {
struct AlignedPlaneRead {
    CastBundle bundle;
    bool frame_aligned{false};
    bool generation_aligned{false};
};
inline AlignedPlaneRead read_aligned(
    Identity cast_id, CoordinateAddress address, TransactionId transaction_id,
    ActivationId activation_id, Value validation_epoch,
    const Plane<DirectionIntent>& p1, const Plane<PossibilitySet>& p2, const Plane<RecoverySet>& p3) {
    AlignedPlaneRead out;
    out.frame_aligned = p1.frame_id()==address.frame_id && p2.frame_id()==address.frame_id && p3.frame_id()==address.frame_id;
    out.generation_aligned = p1.generation()==address.generation && p2.generation()==address.generation && p3.generation()==address.generation;
    out.bundle = {cast_id,address,transaction_id,activation_id,validation_epoch,p1.get(address.coordinate),p2.get(address.coordinate),p3.get(address.coordinate)};
    return out;
}
inline CastResolution resolve_aligned(const AlignedPlaneRead& r) {
    if (!r.frame_aligned || !r.generation_aligned) return {CastResolutionState::InvalidAlignment,{},0};
    return resolve_cast(r.bundle);
}
}
