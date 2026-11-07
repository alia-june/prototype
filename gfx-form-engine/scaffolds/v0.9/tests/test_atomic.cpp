#include <gfx/atomic/types.hpp>
#include <cassert>
int main(){ gfx::Identity id=42; gfx::Code c=7; gfx::Value v=9; gfx::Mask m=3; assert(id==42&&c==7&&v==9&&m==3); }
