#pragma once
#include <gfx/atomic/types.hpp>
#include <optional>
#include <unordered_map>

namespace gfx {
struct MatrixRouteKey {
    Identity matrix_id{};
    Identity cell_id{};
    Generation generation{};
    friend bool operator==(const MatrixRouteKey&, const MatrixRouteKey&) = default;
};
struct MatrixRouteKeyHash {
    std::size_t operator()(const MatrixRouteKey& k) const noexcept {
        return std::hash<Identity>{}(k.matrix_id) ^ (std::hash<Identity>{}(k.cell_id)<<1) ^ (std::hash<Generation>{}(k.generation)<<2);
    }
};
struct MatrixRouteBinding {
    Identity binding_id{};
    Identity matrix_id{};
    Identity cell_id{};
    Identity route_id{};
    Identity recovery_route_id{};
    Generation generation{};
    Mask authority_mask{};
};
class MatrixRouteRegistry {
public:
    bool bind(MatrixRouteBinding binding) {
        MatrixRouteKey key{binding.matrix_id,binding.cell_id,binding.generation};
        return bindings_.emplace(key,std::move(binding)).second;
    }
    std::optional<MatrixRouteBinding> lookup(Identity matrix_id, Identity cell_id, Generation generation) const {
        auto it=bindings_.find({matrix_id,cell_id,generation});
        if(it==bindings_.end()) return std::nullopt;
        return it->second;
    }
private:
    std::unordered_map<MatrixRouteKey,MatrixRouteBinding,MatrixRouteKeyHash> bindings_;
};
}
