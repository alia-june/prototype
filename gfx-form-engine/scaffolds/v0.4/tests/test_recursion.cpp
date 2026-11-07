#include <gfx/molecular/recursion.hpp>
#include <cassert>
int main(){
    gfx::RecursionInvariantSet ok; assert(gfx::govern_recursion(ok)==gfx::RecursionDisposition::Continue);
    ok.progress_valid=false; assert(gfx::govern_recursion(ok)==gfx::RecursionDisposition::EnterRecoveryPlane);
}
