#include <gfx/runtime/execution_envelope.hpp>
#include <cassert>
int main(){
    gfx::ExecutionEnvelope e;
    assert(e.phase()==gfx::ExecutionPhase::Intent);
    assert(!e.advance(gfx::ExecutionPhase::Effect));
    assert(e.advance(gfx::ExecutionPhase::Precheck));
    assert(e.advance(gfx::ExecutionPhase::Effect));
    assert(e.advance(gfx::ExecutionPhase::Complete));
    assert(e.advance(gfx::ExecutionPhase::Commit)); assert(e.committed());
    assert(!e.advance(gfx::ExecutionPhase::Fault));
    gfx::ExecutionEnvelope f; assert(f.advance(gfx::ExecutionPhase::Fault)); assert(f.faulted());
}
