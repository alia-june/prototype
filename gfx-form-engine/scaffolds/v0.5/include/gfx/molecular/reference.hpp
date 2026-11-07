#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
enum class ResolutionState : Code { Unresolved=0, Resolved=1, Missing=2, Stale=3, Forbidden=4 };
enum class ValidationState : Code { Unknown=0, Valid=1, Invalid=2 };

struct Reference {
    Identity reference_id{};
    Identity source_id{};
    Identity target_id{};
    Code reference_kind{};
    Identity scope_id{};
    Identity frame_id{};
    Generation expected_generation{};
    Mask authority_mask{};
    ResolutionState resolution_state{ResolutionState::Unresolved};
    ValidationState validation_state{ValidationState::Unknown};
};

struct ReferenceTargetState {
    Identity target_id{};
    Generation generation{};
    Mask granted_authority{};
    bool exists{false};
};

ValidationState validate_reference(Reference& reference, const ReferenceTargetState& target);
}
