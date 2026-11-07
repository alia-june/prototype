#pragma once
#include <gfx/runtime/checkpoint.hpp>
#include <gfx/runtime/recovery_domain.hpp>
#include <gfx/runtime/route_commit.hpp>
#include <gfx/molecular/route.hpp>

namespace gfx {
enum class RecoveryPlanState : Code {
    Rejected=0,
    Candidate=1,
    AuthorizationRequired=2,
    Authorized=3
};

enum class RecoveryPlanFailure : Code {
    None=0,
    InvalidCheckpoint=1,
    InvalidRoute=2,
    InvalidDomain=3,
    GenerationMismatch=4,
    TransactionMismatch=5,
    RouteNotInDomain=6,
    ActivationNotInDomain=7,
    FrameMismatch=8,
    AuthorizationMismatch=9
};

struct RecoveryPlanCandidate {
    Identity plan_id{};
    Identity checkpoint_id{};
    Identity route_id{};
    Identity recovery_domain_id{};
    Identity recursion_id{};
    ActivationId activation_id{};
    TransactionId transaction_id{};
    Generation generation{};
    RecoveryPlanState state{RecoveryPlanState::Rejected};
    RecoveryPlanFailure failure{RecoveryPlanFailure::None};
};

inline RecoveryPlanCandidate validate_recovery_plan(
    Identity plan_id,
    const RecoveryCheckpoint& checkpoint,
    const Route& route,
    const RecoveryDomain& domain,
    Identity recursion_id,
    TransactionId transaction_id,
    Generation generation) noexcept {
    RecoveryPlanCandidate out{plan_id,checkpoint.checkpoint_id,route.route_id,domain.domain_id,recursion_id,
                              checkpoint.activation_id,transaction_id,generation,RecoveryPlanState::Rejected,
                              RecoveryPlanFailure::None};
    if (!plan_id || !checkpoint.checkpoint_id || checkpoint.validation_mask==0 || checkpoint.recursion_id!=recursion_id) {
        out.failure=RecoveryPlanFailure::InvalidCheckpoint; return out;
    }
    if (!route.route_id || !route.valid_chain() || route.steps.empty()) {
        out.failure=RecoveryPlanFailure::InvalidRoute; return out;
    }
    if (!domain.domain_id || (domain.state!=RecoveryDomainState::Faulted && domain.state!=RecoveryDomainState::Recovering && domain.state!=RecoveryDomainState::Quiesced)) {
        out.failure=RecoveryPlanFailure::InvalidDomain; return out;
    }
    if (checkpoint.generation!=generation || route.generation!=generation || domain.generation!=generation) {
        out.failure=RecoveryPlanFailure::GenerationMismatch; return out;
    }
    if (checkpoint.transaction_id!=transaction_id) {
        out.failure=RecoveryPlanFailure::TransactionMismatch; return out;
    }
    if (!domain.contains_activation(checkpoint.activation_id)) {
        out.failure=RecoveryPlanFailure::ActivationNotInDomain; return out;
    }
    bool route_in_domain=false;
    for (auto id:domain.route_ids) if (id==route.route_id) { route_in_domain=true; break; }
    if (!route_in_domain) { out.failure=RecoveryPlanFailure::RouteNotInDomain; return out; }
    if (checkpoint.address.frame_id!=route.frame_id) { out.failure=RecoveryPlanFailure::FrameMismatch; return out; }
    out.state=RecoveryPlanState::AuthorizationRequired;
    return out;
}

inline RecoveryPlanCandidate authorize_recovery_plan(
    RecoveryPlanCandidate plan, const RecoveryAuthorization& authorization) noexcept {
    if (plan.state!=RecoveryPlanState::AuthorizationRequired || !authorization.approved || !authorization.authority_id ||
        authorization.transaction_id!=plan.transaction_id || authorization.route_id!=plan.route_id ||
        authorization.generation!=plan.generation) {
        plan.state=RecoveryPlanState::Rejected;
        plan.failure=RecoveryPlanFailure::AuthorizationMismatch;
        return plan;
    }
    plan.state=RecoveryPlanState::Authorized;
    plan.failure=RecoveryPlanFailure::None;
    return plan;
}
}
