#include <gfx/structures/backing_pool.hpp>
#include <gfx/molecular/route.hpp>
#include <cassert>
int main(){
 gfx::HomogeneousBackingPool<int> pool; assert(pool.insert(1,42)); assert(!pool.insert(1,99)); assert(pool.find(1)&&*pool.find(1)==42);
 gfx::CoordinateAddress a{10,{0,0,0},3}, b{10,{1,0,0},3}, c{10,{2,0,0},3};
 gfx::Route r{7,10,3,{{1,a,b,11,0,0},{2,b,c,12,0,0}}}; assert(r.valid_chain());
 r.steps[1].source.coordinate={9,0,0}; assert(!r.valid_chain());
}
