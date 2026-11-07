#include <gfx/runtime/integrity_commit_chain.hpp>
#include <cassert>
int main(){
    gfx::TransactionLedger ledger;
    ledger.append({10,100,1,gfx::LedgerPhase::Commit,1});
    ledger.append({11,100,2,gfx::LedgerPhase::Commit,1});
    gfx::IntegrityCommitChain chain;
    auto c1=gfx::make_integrity_certificate(1,0,10,100,1,1,gfx::sha256("payload-one"));
    assert(chain.append(c1,ledger));
    auto c2=gfx::make_integrity_certificate(2,1,11,100,2,1,gfx::sha256("payload-two"),c1.certificate_digest);
    assert(chain.append(c2,ledger));
    assert(chain.valid(ledger));
    auto bad=c2; bad.certificate_id=3; // digest no longer matches fields
    assert(!chain.append(bad,ledger));
    auto wrong_prev=gfx::make_integrity_certificate(3,2,11,100,2,1,gfx::sha256("payload-three"),{});
    assert(!chain.append(wrong_prev,ledger));
}
