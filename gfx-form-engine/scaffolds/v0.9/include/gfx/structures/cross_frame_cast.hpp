#pragma once
#include <gfx/structures/aligned_planes.hpp>
#include <gfx/structures/frame_path.hpp>
#include <optional>

namespace gfx {
enum class CrossFrameCastState : Code { Rejected=0, Mapped=1, Resolved=2 };
struct CrossFrameCastResult {
    CrossFrameCastState state{CrossFrameCastState::Rejected};
    CoordinateAddress source_address{};
    CoordinateAddress mapped_address{};
    std::vector<FrameRelation> mapping_path;
    CastResolution resolution{};
};

inline CrossFrameCastResult resolve_cross_frame_cast(
    Identity cast_id,
    CoordinateAddress source_address,
    Identity destination_frame_id,
    TransactionId transaction_id,
    ActivationId activation_id,
    Value validation_epoch,
    const FrameGraph& frame_graph,
    const FrameMappingRegistry& mapping_registry,
    const Plane<DirectionIntent>& p1,
    const Plane<PossibilitySet>& p2,
    const Plane<RecoverySet>& p3) {
    CrossFrameCastResult out; out.source_address=source_address;
    auto path=frame_graph.path(source_address.frame_id,destination_frame_id);
    if (!path) return out;
    auto mapped=map_frame_path(source_address,*path,mapping_registry);
    if (!mapped) return out;
    out.mapping_path=*path; out.mapped_address=*mapped; out.state=CrossFrameCastState::Mapped;
    const auto aligned=read_aligned(cast_id,*mapped,transaction_id,activation_id,validation_epoch,p1,p2,p3);
    out.resolution=resolve_aligned(aligned);
    if (out.resolution.state==CastResolutionState::Accepted || out.resolution.state==CastResolutionState::RecoveryRequired)
        out.state=CrossFrameCastState::Resolved;
    return out;
}
}
