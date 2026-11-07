#pragma once
#include <gfx/atomic/types.hpp>
#include <vector>
#include <cstddef>

namespace gfx {
enum class LexicalClass : std::uint8_t {
    Ordinary=0, Whitespace, Quote, Escape,
    ObjectOpen, ObjectClose, ArrayOpen, ArrayClose,
    Colon, Comma, Digit, Sign, Decimal, Exponent,
    Letter, Control, NonAscii, Invalid
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
};
}
