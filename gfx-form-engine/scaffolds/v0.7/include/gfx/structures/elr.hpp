#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/backing.hpp>
#include <vector>
#include <cstddef>

namespace gfx {
enum class LexicalClass : std::uint8_t {
    Ordinary=0, Whitespace, Quote, Escape,
    ObjectOpen, ObjectClose, ArrayOpen, ArrayClose,
    Colon, Comma, Digit, Sign, Decimal, Exponent,
    Letter, Control, NonAscii, Invalid
};

enum class ElrPlaneKind : Code { Class=1, Whitespace=2, Escape=3, String=4, Structural=5, Error=6, Depth=7 };
struct ElrPlaneDescriptor {
    Identity plane_id{};
    ElrPlaneKind kind{ElrPlaneKind::Class};
    BackingClass backing_class{BackingClass::Dense};
    Generation source_generation{};
    Generation generation{};
    Length element_count{};
    Value element_width_bits{};
    Mask validation_mask{};
};

struct ElrSource {
    Identity source_id{};
    Generation generation{};
    std::vector<std::byte> bytes;
};

struct Elr {
    Identity elr_id{};
    Identity source_id{};
    Generation source_generation{};
    Generation generation{};
    std::vector<LexicalClass> class_plane;
    std::vector<bool> whitespace_plane;
    std::vector<bool> escape_plane;
    std::vector<bool> string_plane;
    std::vector<bool> structural_plane;
    std::vector<bool> error_plane;
    std::vector<std::uint32_t> depth_plane;
    std::vector<Offset> structural_positions;
    std::vector<ElrPlaneDescriptor> plane_descriptors;
};
}
