#pragma once
#include <gfx/molecular/recursion.hpp>
#include <gfx/structures/cast.hpp>
#include <gfx/runtime/recovery.hpp>
namespace gfx {
enum class RecursionRecoveryReason : Code { None=0, Reference=1, Transition=2, Progress=3, Resource=4, Continuation=5, Cycle=6, Sentinel=7 };
struct RecursionGovernanceResult { RecursionDisposition disposition{RecursionDisposition::Continue}; RecursionRecoveryReason reason{RecursionRecoveryReason::None}; };
inline RecursionGovernanceResult evaluate_recursion(const RecursionInvariantSet& i) noexcept {
    if (!i.reference_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Reference};
    if (!i.transition_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Transition};
    if (!i.progress_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Progress};
    if (!i.resource_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Resource};
    if (!i.continuation_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Continuation};
    if (!i.cycle_policy_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Cycle};
    if (!i.sentinels_valid) return {RecursionDisposition::EnterRecoveryPlane,RecursionRecoveryReason::Sentinel};
    return {};
}
}
