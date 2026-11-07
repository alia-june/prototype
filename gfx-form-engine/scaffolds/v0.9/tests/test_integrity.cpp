#include <gfx/runtime/integrity.hpp>
#include <cassert>
int main(){
    const auto d=gfx::sha256("abc");
    assert(gfx::digest_hex(d)=="ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    assert(!gfx::digest_is_zero(d));
    const gfx::Digest256 zero{}; assert(gfx::digest_is_zero(zero));
}
