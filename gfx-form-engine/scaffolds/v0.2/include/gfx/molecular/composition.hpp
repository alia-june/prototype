#pragma once
#include <gfx/atomic/types.hpp>
#include <vector>
namespace gfx {
struct Composition {
    Identity composition_id{};
    Identity product_id{};
    std::vector<Identity> component_reference_ids;
    std::vector<Identity> relation_ids;
};
struct Decomposition {
    Identity decomposition_id{};
    Identity subject_id{};
    std::vector<Identity> component_reference_ids;
    std::vector<Identity> relation_ids;
};
}
