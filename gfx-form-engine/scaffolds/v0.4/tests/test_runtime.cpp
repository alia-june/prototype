#include <gfx/runtime/identity.hpp>
#include <gfx/runtime/generation.hpp>
#include <gfx/runtime/ledger.hpp>
#include <gfx/structures/brick.hpp>
#include <gfx/structures/traversal.hpp>
#include <cassert>
int main(){
  gfx::IdentityAllocator ids(10); assert(ids.next()==10); assert(ids.next()==11);
  gfx::GenerationRegistry gr; gr.publish(5,7); assert(gr.matches(5,7)); assert(!gr.matches(5,6));
  gfx::TransactionLedger ledger; ledger.append({1,5,7,gfx::LedgerPhase::Prepare,0}); assert(!ledger.has_commit(1,7)); ledger.append({1,5,7,gfx::LedgerPhase::Commit,0}); assert(ledger.has_commit(1,7));
  gfx::Brick<int,4> b; b.set(1,2,3,99); assert(b.get(1,2,3).value()==99); assert(!b.get(0,0,0));
  gfx::DdaState d{{0,0,0},0.2,0.5,0.8,1,1,1,1,1,1}; const gfx::Coordinate expected{1,0,0}; assert(gfx::dda_step(d)==expected);
}
