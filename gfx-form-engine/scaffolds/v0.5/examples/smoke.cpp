#include <gfx/workloads/json0/lexical.hpp>
#include <iostream>
int main() {
    auto r = gfx::json0::build_elr(R"({"a":[1,true,{"b":"c"}]})");
    std::cout << "structural_positions=" << r.elr.structural_positions.size() << "\n";
    std::cout << "strings_balanced=" << r.strings_balanced << " structure_balanced=" << r.structure_balanced << "\n";
}
