#pragma once
#include <gfx/atomic/types.hpp>
#include <algorithm>
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

struct CompositionCheck {
    bool subject_matches{false};
    bool components_match{false};
    bool relations_match{false};
    [[nodiscard]] bool equivalent() const noexcept {
        return subject_matches && components_match && relations_match;
    }
};

inline std::vector<Identity> normalized_id_set(std::vector<Identity> ids) {
    std::sort(ids.begin(), ids.end());
    ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
    return ids;
}

inline CompositionCheck validate_round_trip(const Composition& composition, const Decomposition& decomposition) {
    return {
        composition.product_id == decomposition.subject_id,
        normalized_id_set(composition.component_reference_ids) == normalized_id_set(decomposition.component_reference_ids),
        normalized_id_set(composition.relation_ids) == normalized_id_set(decomposition.relation_ids)
    };
}
}
