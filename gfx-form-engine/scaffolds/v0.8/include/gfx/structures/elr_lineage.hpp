#pragma once
#include <gfx/atomic/types.hpp>
#include <vector>

namespace gfx {
enum class ElrStage : Code { Source=1, Classify=2, Escape=3, String=4, Structure=5, Depth=6, Compact=7, Validate=8 };
struct ElrGenerationRecord {
    Identity record_id{};
    Identity elr_id{};
    ElrStage stage{ElrStage::Source};
    Generation generation{};
    Generation parent_generation{};
    Identity operation_id{};
    Mask validation_mask{};
};
class ElrLineage {
public:
    bool append(ElrGenerationRecord record) {
        if (!record.record_id || !record.elr_id || !record.generation) return false;
        if (!records_.empty()) {
            const auto& previous=records_.back();
            if (record.elr_id!=previous.elr_id || record.parent_generation!=previous.generation) return false;
        } else if (record.parent_generation!=0) return false;
        records_.push_back(record); return true;
    }
    [[nodiscard]] bool valid() const noexcept {
        Generation previous{}; Identity elr{};
        for (std::size_t i=0;i<records_.size();++i) {
            const auto& r=records_[i];
            if (!r.record_id || !r.elr_id || !r.generation) return false;
            if (i==0) { if (r.parent_generation!=0) return false; elr=r.elr_id; }
            else if (r.elr_id!=elr || r.parent_generation!=previous) return false;
            previous=r.generation;
        }
        return true;
    }
    [[nodiscard]] const std::vector<ElrGenerationRecord>& records() const noexcept { return records_; }
private:
    std::vector<ElrGenerationRecord> records_;
};
}
