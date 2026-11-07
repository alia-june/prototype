#pragma once
#include <gfx/atomic/types.hpp>

namespace gfx {
enum class ExecutionPhase : Code { Intent=0, Precheck=1, Effect=2, Complete=3, Commit=4, Fault=5 };

class ExecutionEnvelope {
public:
    [[nodiscard]] ExecutionPhase phase() const noexcept { return phase_; }
    [[nodiscard]] bool committed() const noexcept { return phase_==ExecutionPhase::Commit; }
    [[nodiscard]] bool faulted() const noexcept { return phase_==ExecutionPhase::Fault; }

    bool advance(ExecutionPhase next) noexcept {
        if (phase_==ExecutionPhase::Fault || phase_==ExecutionPhase::Commit) return false;
        if (next==ExecutionPhase::Fault) { phase_=next; return true; }
        const auto expected = static_cast<Code>(phase_) + 1;
        if (static_cast<Code>(next)!=expected) return false;
        phase_=next; return true;
    }
private:
    ExecutionPhase phase_{ExecutionPhase::Intent};
};
}
