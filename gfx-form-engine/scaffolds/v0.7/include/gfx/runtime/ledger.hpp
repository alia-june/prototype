#pragma once
#include <gfx/atomic/types.hpp>
#include <vector>
namespace gfx {
enum class LedgerPhase : Code { Prepare=1, Commit=2, Publish=3, Retire=4 };
struct LedgerRecord { TransactionId transaction_id{}; Identity subject_id{}; Generation generation{}; LedgerPhase phase{LedgerPhase::Prepare}; Mask validation_mask{}; };
class TransactionLedger {
public:
    void append(LedgerRecord r) { records_.push_back(r); }
    bool has_phase(TransactionId tx, Generation generation, LedgerPhase phase) const {
        for (const auto& r: records_) if (r.transaction_id==tx && r.generation==generation && r.phase==phase) return true;
        return false;
    }
    bool has_commit(TransactionId tx, Generation generation) const { return has_phase(tx,generation,LedgerPhase::Commit); }
    const std::vector<LedgerRecord>& records() const noexcept { return records_; }
private:
    std::vector<LedgerRecord> records_;
};
}
