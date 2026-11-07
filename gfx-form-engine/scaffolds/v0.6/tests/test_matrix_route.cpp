#include <gfx/structures/matrix.hpp>
#include <gfx/structures/matrix_route.hpp>
#include <cassert>
int main(){
    gfx::ExecutionMatrix matrix; matrix.bind({1,2,3},{41,51,61,0,0,0,0,0,0});
    auto cell=matrix.lookup({1,2,3}); assert(cell && cell->cell_id==41);
    gfx::MatrixRouteRegistry routes; assert(routes.bind({100,9,41,700,701,5,0x3}));
    auto binding=routes.lookup(9,cell->cell_id,5); assert(binding && binding->route_id==700 && binding->recovery_route_id==701);
    assert(!routes.lookup(9,41,4));
}
