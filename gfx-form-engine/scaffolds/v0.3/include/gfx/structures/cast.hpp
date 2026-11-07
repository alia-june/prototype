#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <gfx/structures/plane.hpp>
#include <optional>
#include <vector>

namespace gfx {
struct DirectionIntent { Direction direction{}; Coordinate proposed_target{}; Code local_state{}; Value priority{}; };
struct Possibility { Direction direction{}; Coordinate target{}; Code required_state{}; Code required_operation{}; };
struct PossibilitySet { std::vector<Possibility> allowed; Mask authority_mask{}; };
struct RecoveryOption { Code condition_code{}; Coordinate target{}; Code operation_code{}; Mask authority_mask{}; Value priority{}; };
struct RecoverySet { std::vector<RecoveryOption> options; };

enum class CastResolutionState : Code { Accepted=0, RecoveryRequired=1, InvalidAlignment=2, MissingData=3 };
struct CastBundle {
    Identity cast_id{};
    CoordinateAddress address{};
    TransactionId transaction_id{};
    ActivationId activation_id{};
    Value validation_epoch{};
    std::optional<DirectionIntent> plane1;
    std::optional<PossibilitySet> plane2;
    std::optional<RecoverySet> plane3;
};
struct CastResolution { CastResolutionState state{CastResolutionState::MissingData}; Coordinate selected_target{}; Mask sentinel_mask{}; };

inline bool same_direction(const Direction& a, const Direction& b) { return a.dx==b.dx && a.dy==b.dy && a.dz==b.dz; }
inline CastResolution resolve_cast(const CastBundle& b) {
    if (!b.plane1 || !b.plane2 || !b.plane3) return {};
    for (const auto& p : b.plane2->allowed) {
        if (same_direction(p.direction, b.plane1->direction) && p.target == b.plane1->proposed_target)
            return {CastResolutionState::Accepted, p.target, 0};
    }
    return {CastResolutionState::RecoveryRequired, {}, 0};
}
}
