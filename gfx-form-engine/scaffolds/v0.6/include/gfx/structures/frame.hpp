#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <array>
namespace gfx {
struct Frame {
    Identity frame_id{};
    Identity x_function_id{};
    Identity y_function_id{};
    Identity z_function_id{};
    Identity relation_schema_id{};
    Identity transform_set_id{};
    Generation generation{};
};

enum class MappingKind : Code { Reindex=0, SemanticProjection=1 };
struct FrameMapping {
    Identity mapping_id{};
    Identity source_frame_id{};
    Identity destination_frame_id{};
    MappingKind kind{MappingKind::Reindex};
    bool reversible{false};
    Mask validation_mask{};
};
}
