#pragma once
#include <gfx/workloads/json0/parser.hpp>
#include <string>

namespace gfx::json0 {
inline std::string reconstruct_source(const JsonDocument& document) { return document.source_text; }
inline bool validate_round_trip(const JsonDocument& document) {
    if (!document.valid()) return false;
    const auto reconstructed = reconstruct_source(document);
    const auto reparsed = parse(reconstructed, document.source_id, document.generation);
    return reparsed.valid() && reparsed.source_text == document.source_text &&
           reparsed.nodes.size()==document.nodes.size() && reparsed.data.size()==document.data.size() &&
           reparsed.relations.size()==document.relations.size() && reparsed.sequence.size()==document.sequence.size();
}
}
