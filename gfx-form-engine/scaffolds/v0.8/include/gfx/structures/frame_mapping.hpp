#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <gfx/molecular/reference.hpp>
#include <array>
#include <optional>
#include <vector>

namespace gfx {

// ReindexTransform changes coordinate representation without assigning semantic meaning
// to X/Y/Z. Each destination axis selects one distinct source axis, applies sign, then offset.
struct ReindexTransform {
    std::array<std::uint8_t,3> source_axis{0,1,2};
    std::array<std::int8_t,3> sign{1,1,1};
    Coordinate offset{};

    [[nodiscard]] bool valid() const noexcept {
        const bool permutation = source_axis[0] < 3 && source_axis[1] < 3 && source_axis[2] < 3 &&
            source_axis[0] != source_axis[1] && source_axis[0] != source_axis[2] && source_axis[1] != source_axis[2];
        const bool signs = (sign[0] == 1 || sign[0] == -1) && (sign[1] == 1 || sign[1] == -1) && (sign[2] == 1 || sign[2] == -1);
        return permutation && signs;
    }

    [[nodiscard]] Coordinate apply(Coordinate source) const noexcept {
        const std::array<std::int64_t,3> v{source.x,source.y,source.z};
        return {
            sign[0] * v[source_axis[0]] + offset.x,
            sign[1] * v[source_axis[1]] + offset.y,
            sign[2] * v[source_axis[2]] + offset.z
        };
    }

    [[nodiscard]] std::optional<Coordinate> inverse(Coordinate destination) const noexcept {
        if (!valid()) return std::nullopt;
        const std::array<std::int64_t,3> d{destination.x-offset.x,destination.y-offset.y,destination.z-offset.z};
        std::array<std::int64_t,3> s{};
        for (std::size_t out=0; out<3; ++out) s[source_axis[out]] = sign[out] * d[out];
        return Coordinate{s[0],s[1],s[2]};
    }
};

enum class ProjectionLoss : Code { None=0, Declared=1 };

struct SemanticProjection {
    Identity projection_id{};
    Identity source_frame_id{};
    Identity destination_frame_id{};
    std::vector<Identity> retained_relation_ids;
    std::vector<Identity> discarded_relation_ids;
    ProjectionLoss loss{ProjectionLoss::Declared};
    Identity provenance_id{};
    ValidationState validation_state{ValidationState::Unknown};
};

struct FrameTransformBinding {
    Identity mapping_id{};
    Identity source_frame_id{};
    Identity destination_frame_id{};
    ReindexTransform transform{};
    Generation generation{};
    ValidationState validation_state{ValidationState::Unknown};
};

inline std::optional<CoordinateAddress> map_address(const CoordinateAddress& address, const FrameTransformBinding& binding) {
    if (binding.validation_state != ValidationState::Valid || !binding.transform.valid() ||
        address.frame_id != binding.source_frame_id || address.generation != binding.generation) return std::nullopt;
    return CoordinateAddress{binding.destination_frame_id,binding.transform.apply(address.coordinate),address.generation};
}
}
