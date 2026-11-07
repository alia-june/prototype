#include <gfx/workloads/json0/reconstruct.hpp>
#include <cassert>
int main(){
    const std::string source=" {\"a\":[1,true,{\"b\":\"x\\\\y\"}],\"n\":null} \n";
    const auto document=gfx::json0::parse(source,77,4);
    assert(document.valid());
    assert(gfx::json0::reconstruct_source(document)==source);
    assert(gfx::json0::validate_round_trip(document));
}
