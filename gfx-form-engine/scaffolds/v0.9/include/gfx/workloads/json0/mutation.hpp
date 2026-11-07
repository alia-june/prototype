#pragma once
#include <gfx/workloads/json0/parser.hpp>
#include <gfx/structures/elr.hpp>
#include <algorithm>
#include <optional>
#include <string>
#include <vector>

namespace gfx::json0 {
struct SourceEdit {
    Offset offset{};
    Length length{};
    std::string replacement;
};

struct SourceMutationPlan {
    Identity plan_id{};
    Identity source_id{};
    Generation expected_generation{};
    Generation target_generation{};
    std::vector<SourceEdit> edits;
};

enum class MutationValidation : Code {
    Valid=0,
    WrongSource=1,
    StaleGeneration=2,
    InvalidTargetGeneration=3,
    OutOfBounds=4,
    Overlap=5
};

inline MutationValidation validate_mutation_plan(const JsonDocument& document, const SourceMutationPlan& plan) {
    if (!plan.plan_id || plan.source_id!=document.source_id) return MutationValidation::WrongSource;
    if (plan.expected_generation!=document.generation) return MutationValidation::StaleGeneration;
    if (plan.target_generation<=plan.expected_generation) return MutationValidation::InvalidTargetGeneration;
    auto edits=plan.edits;
    std::sort(edits.begin(),edits.end(),[](const SourceEdit& a,const SourceEdit& b){return a.offset<b.offset;});
    Offset previous_end{}; bool first=true;
    for (const auto& edit:edits) {
        if (edit.offset>document.source_text.size() || edit.length>document.source_text.size()-edit.offset) return MutationValidation::OutOfBounds;
        if (!first && edit.offset<previous_end) return MutationValidation::Overlap;
        previous_end=edit.offset+edit.length; first=false;
    }
    return MutationValidation::Valid;
}

inline std::optional<std::string> reconstruct_mutated_source(const JsonDocument& document, const SourceMutationPlan& plan) {
    if (validate_mutation_plan(document,plan)!=MutationValidation::Valid) return std::nullopt;
    auto edits=plan.edits;
    std::sort(edits.begin(),edits.end(),[](const SourceEdit& a,const SourceEdit& b){return a.offset<b.offset;});
    std::string out; out.reserve(document.source_text.size());
    Offset cursor{};
    for (const auto& edit:edits) {
        out.append(document.source_text.substr(static_cast<std::size_t>(cursor),static_cast<std::size_t>(edit.offset-cursor)));
        out.append(edit.replacement);
        cursor=edit.offset+edit.length;
    }
    out.append(document.source_text.substr(static_cast<std::size_t>(cursor)));
    return out;
}

inline std::optional<JsonDocument> apply_mutation(const JsonDocument& document, const SourceMutationPlan& plan) {
    const auto source=reconstruct_mutated_source(document,plan); if(!source) return std::nullopt;
    auto next=parse(*source,document.source_id,plan.target_generation);
    if (!next.valid()) return std::nullopt;
    return next;
}

struct ElrRebuildRequest {
    Identity request_id{};
    Identity elr_id{};
    Identity source_id{};
    Generation expected_source_generation{};
    Generation target_source_generation{};
    bool full_rebuild_required{true};
};

inline std::optional<ElrRebuildRequest> plan_elr_rebuild(
    Identity request_id, const Elr& elr, const SourceMutationPlan& mutation) noexcept {
    if (!request_id || elr.source_id!=mutation.source_id || elr.source_generation!=mutation.expected_generation ||
        mutation.target_generation<=mutation.expected_generation) return std::nullopt;
    return ElrRebuildRequest{request_id,elr.elr_id,elr.source_id,mutation.expected_generation,mutation.target_generation,true};
}
}
