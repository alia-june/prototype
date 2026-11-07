#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/runtime/ledger.hpp>
#include <optional>
#include <vector>

namespace gfx {
struct CommitCertificate {
    Identity certificate_id{};
    Identity previous_certificate_id{};
    TransactionId transaction_id{};
    Identity subject_id{};
    Generation generation{};
    Mask validation_mask{};
};

class CommitChain {
public:
    bool append(CommitCertificate certificate, const TransactionLedger& ledger) {
        if (!certificate.certificate_id || !certificate.transaction_id || !certificate.generation || !certificate.validation_mask) return false;
        if (!ledger.has_commit(certificate.transaction_id, certificate.generation)) return false;
        if (certificates_.empty()) {
            if (certificate.previous_certificate_id != 0) return false;
        } else if (certificate.previous_certificate_id != certificates_.back().certificate_id) {
            return false;
        }
        for (const auto& current : certificates_) if (current.certificate_id == certificate.certificate_id) return false;
        certificates_.push_back(certificate);
        return true;
    }

    [[nodiscard]] bool valid(const TransactionLedger& ledger) const noexcept {
        Identity previous{};
        for (const auto& certificate : certificates_) {
            if (!certificate.certificate_id || !certificate.transaction_id || !certificate.generation || !certificate.validation_mask) return false;
            if (certificate.previous_certificate_id != previous) return false;
            if (!ledger.has_commit(certificate.transaction_id, certificate.generation)) return false;
            previous = certificate.certificate_id;
        }
        return true;
    }

    [[nodiscard]] const CommitCertificate* latest() const noexcept {
        return certificates_.empty() ? nullptr : &certificates_.back();
    }

    [[nodiscard]] const std::vector<CommitCertificate>& certificates() const noexcept { return certificates_; }

private:
    std::vector<CommitCertificate> certificates_;
};
}
