#include <gfx/molecular/reference.hpp>
namespace gfx {
ValidationState validate_reference(Reference& r, const ReferenceTargetState& t) {
    if (!t.exists || t.target_id != r.target_id) {
        r.resolution_state = ResolutionState::Missing;
        return r.validation_state = ValidationState::Invalid;
    }
    if (r.expected_generation != 0 && r.expected_generation != t.generation) {
        r.resolution_state = ResolutionState::Stale;
        return r.validation_state = ValidationState::Invalid;
    }
    if ((r.authority_mask & t.granted_authority) != r.authority_mask) {
        r.resolution_state = ResolutionState::Forbidden;
        return r.validation_state = ValidationState::Invalid;
    }
    r.resolution_state = ResolutionState::Resolved;
    return r.validation_state = ValidationState::Valid;
}
}
