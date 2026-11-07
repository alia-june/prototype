#pragma once
#include <gfx/structures/fragment.hpp>
#include <gfx/workloads/json0/lexical.hpp>
#include <string_view>

namespace gfx::json0 {
struct LexicalFragmentValue {
    unsigned char source_byte{};
    LexicalClass lexical_class{LexicalClass::Ordinary};
    bool require_structural{false};
};
using LexicalFragment = gfx::FormFragment<LexicalFragmentValue>;

inline bool match_fragment(const LexicalFragment& fragment, std::string_view source, const Elr& elr, Offset origin) {
    if(fragment.generation!=0 && fragment.generation!=elr.generation) return false;
    for(const auto& r:fragment.requirements) {
        if(r.local_coordinate.y!=0 || r.local_coordinate.z!=0 || r.local_coordinate.x<0) return false;
        const auto p=origin+static_cast<Offset>(r.local_coordinate.x);
        if(p>=source.size() || p>=elr.class_plane.size()) return false;
        if(static_cast<unsigned char>(source[static_cast<std::size_t>(p)])!=r.expected.source_byte) return false;
        if(elr.class_plane[static_cast<std::size_t>(p)]!=r.expected.lexical_class) return false;
        if(r.expected.require_structural && !elr.structural_plane[static_cast<std::size_t>(p)]) return false;
    }
    return true;
}
inline LexicalFragment literal_fragment(Identity id, std::string_view literal, Generation generation=0) {
    LexicalFragment f; f.fragment_id=id; f.generation=generation;
    for(std::size_t i=0;i<literal.size();++i)
        f.requirements.push_back({{static_cast<std::int64_t>(i),0,0},{static_cast<unsigned char>(literal[i]),classify_byte(static_cast<unsigned char>(literal[i])),false},0});
    return f;
}
}
