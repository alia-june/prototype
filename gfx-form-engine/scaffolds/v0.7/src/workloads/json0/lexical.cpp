#include <gfx/workloads/json0/lexical.hpp>
#include <cctype>
#include <vector>

namespace gfx::json0 {
LexicalClass classify_byte(unsigned char c) noexcept {
    switch(c) {
        case ' ': case '\t': case '\r': case '\n': return LexicalClass::Whitespace;
        case '"': return LexicalClass::Quote;
        case '\\': return LexicalClass::Escape;
        case '{': return LexicalClass::ObjectOpen;
        case '}': return LexicalClass::ObjectClose;
        case '[': return LexicalClass::ArrayOpen;
        case ']': return LexicalClass::ArrayClose;
        case ':': return LexicalClass::Colon;
        case ',': return LexicalClass::Comma;
        case '-': return LexicalClass::Sign;
        case '.': return LexicalClass::Decimal;
        case 'e': case 'E': return LexicalClass::Exponent;
        default:
            if (c < 0x20) return LexicalClass::Control;
            if (c >= 0x80) return LexicalClass::NonAscii;
            if (std::isdigit(c)) return LexicalClass::Digit;
            if (std::isalpha(c)) return LexicalClass::Letter;
            return LexicalClass::Ordinary;
    }
}

Json0Result build_elr(std::string_view source, Identity source_id, Generation generation) {
    Json0Result out;
    auto& e = out.elr;
    e.elr_id = 1; e.source_id = source_id; e.source_generation = generation; e.generation = generation;
    const auto n = source.size();
    e.class_plane.resize(n);
    e.whitespace_plane.assign(n,false);
    e.escape_plane.assign(n,false);
    e.string_plane.assign(n,false);
    e.structural_plane.assign(n,false);
    e.error_plane.assign(n,false);
    e.depth_plane.assign(n,0);
    e.plane_descriptors = {
        {1,ElrPlaneKind::Class,BackingClass::Dense,generation,generation,(Length)n,8,0},
        {2,ElrPlaneKind::Whitespace,BackingClass::Dense,generation,generation,(Length)n,1,0},
        {3,ElrPlaneKind::Escape,BackingClass::Dense,generation,generation,(Length)n,1,0},
        {4,ElrPlaneKind::String,BackingClass::Dense,generation,generation,(Length)n,1,0},
        {5,ElrPlaneKind::Structural,BackingClass::Dense,generation,generation,(Length)n,1,0},
        {6,ElrPlaneKind::Error,BackingClass::Dense,generation,generation,(Length)n,1,0},
        {7,ElrPlaneKind::Depth,BackingClass::Dense,generation,generation,(Length)n,32,0}
    };

    bool in_string = false;
    std::size_t backslash_run = 0;
    std::uint32_t depth = 0;
    std::vector<LexicalClass> container_stack;

    for (std::size_t i=0;i<n;++i) {
        const auto c = static_cast<unsigned char>(source[i]);
        const auto cls = classify_byte(c);
        e.class_plane[i] = cls;
        e.whitespace_plane[i] = cls == LexicalClass::Whitespace;

        bool escaped = false;
        if (c == '\\') {
            ++backslash_run;
        } else {
            escaped = (backslash_run % 2) == 1;
            backslash_run = 0;
        }
        e.escape_plane[i] = escaped;

        if (cls == LexicalClass::Quote && !escaped) in_string = !in_string;
        e.string_plane[i] = in_string || cls == LexicalClass::Quote;

        const bool structural_candidate = cls==LexicalClass::ObjectOpen || cls==LexicalClass::ObjectClose ||
            cls==LexicalClass::ArrayOpen || cls==LexicalClass::ArrayClose || cls==LexicalClass::Colon || cls==LexicalClass::Comma;
        const bool structural = structural_candidate && !in_string;
        e.structural_plane[i] = structural;

        if (!in_string && (cls==LexicalClass::ObjectClose || cls==LexicalClass::ArrayClose)) {
            const auto expected = cls==LexicalClass::ObjectClose ? LexicalClass::ObjectOpen : LexicalClass::ArrayOpen;
            if (depth==0 || container_stack.empty() || container_stack.back()!=expected) {
                e.error_plane[i]=true; out.structure_balanced=false;
                if (depth>0) --depth;
                if (!container_stack.empty()) container_stack.pop_back();
            } else {
                --depth; container_stack.pop_back();
            }
        }
        e.depth_plane[i] = depth;
        if (structural) {
            e.structural_positions.push_back(static_cast<Offset>(i));
            out.structure.push_back({static_cast<Offset>(i), cls, depth});
        }
        if (!in_string && (cls==LexicalClass::ObjectOpen || cls==LexicalClass::ArrayOpen)) {
            container_stack.push_back(cls); ++depth;
        }
        if (in_string && cls==LexicalClass::Control) e.error_plane[i] = true;
    }

    out.strings_balanced = !in_string;
    if (in_string && n) e.error_plane[n-1] = true;
    if (depth != 0 || !container_stack.empty()) out.structure_balanced = false;
    return out;
}
}
