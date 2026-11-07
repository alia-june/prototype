#pragma once
#include <gfx/structures/elr.hpp>
#include <string_view>
#include <vector>

namespace gfx::json0 {
struct StructuralElement { Offset offset{}; LexicalClass type{LexicalClass::Ordinary}; std::uint32_t depth{}; };
struct Json0Result {
    Elr elr;
    std::vector<StructuralElement> structure;
    bool strings_balanced{true};
    bool structure_balanced{true};
};
LexicalClass classify_byte(unsigned char c) noexcept;
Json0Result build_elr(std::string_view source, Identity source_id=1, Generation generation=1);
}
