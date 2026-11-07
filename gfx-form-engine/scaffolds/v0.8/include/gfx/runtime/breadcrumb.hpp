#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/runtime/execution_envelope.hpp>
#include <gfx/structures/coordinate.hpp>
#include <vector>

namespace gfx {
struct Breadcrumb {
    Sequence sequence{};
    TransactionId transaction_id{};
    ActivationId activation_id{};
    Identity frame_id{};
    Coordinate coordinate{};
    Generation generation{};
    Code opcode{};
    ExecutionPhase phase{ExecutionPhase::Intent};
    Mask sentinel_summary{};
};

class BreadcrumbRing {
public:
    explicit BreadcrumbRing(std::size_t capacity) : capacity_(capacity) { entries_.reserve(capacity); }
    bool push(Breadcrumb b) {
        if (!capacity_) return false;
        if (entries_.size()<capacity_) entries_.push_back(std::move(b));
        else { entries_[next_]=std::move(b); next_=(next_+1)%capacity_; wrapped_=true; }
        return true;
    }
    [[nodiscard]] std::vector<Breadcrumb> snapshot() const {
        if (!wrapped_) return entries_;
        std::vector<Breadcrumb> out; out.reserve(entries_.size());
        for (std::size_t i=0;i<entries_.size();++i) out.push_back(entries_[(next_+i)%entries_.size()]);
        return out;
    }
    [[nodiscard]] std::size_t capacity() const noexcept { return capacity_; }
private:
    std::size_t capacity_{}; std::size_t next_{}; bool wrapped_{}; std::vector<Breadcrumb> entries_;
};
}
