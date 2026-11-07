#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/molecular/route.hpp>
#include <gfx/runtime/ledger.hpp>

namespace gfx {
enum class RouteCommitState : Code { Rejected=0, Prepared=1, Committed=2, RecoveryAuthorizationRequired=3 };
struct RecoveryAuthorization {
    Identity authority_id{};
    TransactionId transaction_id{};
    Identity route_id{};
    Generation generation{};
    Mask scope_mask{};
    bool approved{false};
};
struct RouteCommitResult {
    RouteCommitState state{RouteCommitState::Rejected};
    Identity route_id{};
    TransactionId transaction_id{};
    Generation generation{};
};
inline RouteCommitResult prepare_route(TransactionLedger& ledger, TransactionId tx, Identity subject_id, const Route& route, Mask validation_mask) {
    if(!route.valid_chain() || validation_mask==0) return {};
    ledger.append({tx,subject_id,route.generation,LedgerPhase::Prepare,validation_mask});
    return {RouteCommitState::Prepared,route.route_id,tx,route.generation};
}
inline RouteCommitResult commit_route(TransactionLedger& ledger, TransactionId tx, Identity subject_id, const Route& route, Mask validation_mask) {
    if(!route.valid_chain() || validation_mask==0 || !ledger.has_phase(tx,route.generation,LedgerPhase::Prepare)) return {};
    ledger.append({tx,subject_id,route.generation,LedgerPhase::Commit,validation_mask});
    return {RouteCommitState::Committed,route.route_id,tx,route.generation};
}
inline RouteCommitResult commit_recovery_route(TransactionLedger& ledger, TransactionId tx, Identity subject_id, const Route& route,
                                                Mask validation_mask, const RecoveryAuthorization& authorization) {
    if(!authorization.approved || authorization.authority_id==0 || authorization.transaction_id!=tx ||
       authorization.route_id!=route.route_id || authorization.generation!=route.generation)
        return {RouteCommitState::RecoveryAuthorizationRequired,route.route_id,tx,route.generation};
    return commit_route(ledger,tx,subject_id,route,validation_mask);
}
}
