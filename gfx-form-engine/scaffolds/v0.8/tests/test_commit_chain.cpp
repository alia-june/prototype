#include <gfx/runtime/commit_chain.hpp>
#include <cassert>
int main(){
    gfx::TransactionLedger ledger;
    ledger.append({10,20,1,gfx::LedgerPhase::Prepare,1});
    ledger.append({10,20,1,gfx::LedgerPhase::Commit,1});
    ledger.append({11,20,2,gfx::LedgerPhase::Prepare,1});
    ledger.append({11,20,2,gfx::LedgerPhase::Commit,1});
    gfx::CommitChain chain;
    assert(chain.append({100,0,10,20,1,1},ledger));
    assert(chain.append({101,100,11,20,2,1},ledger));
    assert(chain.valid(ledger));
    assert(chain.latest() && chain.latest()->generation==2);
    assert(!chain.append({102,999,11,20,2,1},ledger));
}
