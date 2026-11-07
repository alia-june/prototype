#pragma once
#include <gfx/atomic/types.hpp>
#include <atomic>
namespace gfx {
class IdentityAllocator {
public:
    explicit IdentityAllocator(Identity start=1) : next_(start) {}
    Identity next() noexcept { return next_.fetch_add(1, std::memory_order_relaxed); }
private:
    std::atomic<Identity> next_;
};
}
