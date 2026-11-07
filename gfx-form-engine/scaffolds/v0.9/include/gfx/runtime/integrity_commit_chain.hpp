#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/runtime/integrity.hpp>
#include <gfx/runtime/ledger.hpp>
#include <vector>

namespace gfx {
struct IntegrityCommitCertificate {
    Identity certificate_id{};
    Identity previous_certificate_id{};
    TransactionId transaction_id{};
    Identity subject_id{};
    Generation generation{};
    Mask validation_mask{};
    Digest256 payload_digest{};
    Digest256 previous_certificate_digest{};
    Digest256 certificate_digest{};
};

inline Digest256 calculate_certificate_digest(const IntegrityCommitCertificate& c) {
    std::vector<std::byte> data;
    data.reserve(8*6+64);
    append_u64_be(data,c.certificate_id);
    append_u64_be(data,c.previous_certificate_id);
    append_u64_be(data,c.transaction_id);
    append_u64_be(data,c.subject_id);
    append_u64_be(data,c.generation);
    append_u64_be(data,c.validation_mask);
    append_digest(data,c.payload_digest);
    append_digest(data,c.previous_certificate_digest);
    return sha256(data);
}

inline IntegrityCommitCertificate make_integrity_certificate(
    Identity certificate_id, Identity previous_certificate_id, TransactionId transaction_id,
    Identity subject_id, Generation generation, Mask validation_mask,
    Digest256 payload_digest, Digest256 previous_certificate_digest={}) {
    IntegrityCommitCertificate c{certificate_id,previous_certificate_id,transaction_id,subject_id,generation,
                                 validation_mask,payload_digest,previous_certificate_digest,{}};
    c.certificate_digest=calculate_certificate_digest(c);
    return c;
}

class IntegrityCommitChain {
public:
    bool append(IntegrityCommitCertificate certificate, const TransactionLedger& ledger) {
        if (!certificate.certificate_id || !certificate.transaction_id || !certificate.generation || !certificate.validation_mask) return false;
        if (digest_is_zero(certificate.payload_digest) || certificate.certificate_digest!=calculate_certificate_digest(certificate)) return false;
        if (!ledger.has_commit(certificate.transaction_id,certificate.generation)) return false;
        if (certificates_.empty()) {
            if (certificate.previous_certificate_id!=0 || !digest_is_zero(certificate.previous_certificate_digest)) return false;
        } else {
            const auto& prior=certificates_.back();
            if (certificate.previous_certificate_id!=prior.certificate_id || certificate.previous_certificate_digest!=prior.certificate_digest) return false;
        }
        for (const auto& existing:certificates_) if (existing.certificate_id==certificate.certificate_id) return false;
        certificates_.push_back(std::move(certificate));
        return true;
    }

    [[nodiscard]] bool valid(const TransactionLedger& ledger) const noexcept {
        Identity prior_id{}; Digest256 prior_digest{};
        for (const auto& c:certificates_) {
            if (!c.certificate_id || !c.transaction_id || !c.generation || !c.validation_mask) return false;
            if (c.previous_certificate_id!=prior_id || c.previous_certificate_digest!=prior_digest) return false;
            if (c.certificate_digest!=calculate_certificate_digest(c)) return false;
            if (!ledger.has_commit(c.transaction_id,c.generation)) return false;
            prior_id=c.certificate_id; prior_digest=c.certificate_digest;
        }
        return true;
    }
    [[nodiscard]] const std::vector<IntegrityCommitCertificate>& certificates() const noexcept { return certificates_; }
private:
    std::vector<IntegrityCommitCertificate> certificates_;
};
}
