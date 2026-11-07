#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
enum class RecoveryDecision : Code { Retry=0, Rollback=1, Reload=2, Quarantine=3, Halt=4, Reauthorize=5 };
struct RecoveryRequest {
    Identity recovery_set_id{};
    Identity recursion_id{};
    Generation generation{};
    Code failure_code{};
};
class CpuRecoveryAuthority {
public:
    virtual ~CpuRecoveryAuthority() = default;
    virtual RecoveryDecision decide(const RecoveryRequest&) = 0;
};
}
