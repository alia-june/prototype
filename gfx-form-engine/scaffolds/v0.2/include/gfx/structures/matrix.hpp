#pragma once
#include <gfx/atomic/types.hpp>
#include <unordered_map>
#include <optional>
namespace gfx {
struct MatrixKey { Code state{}; Code opcode{}; Code selector{}; friend bool operator==(const MatrixKey&, const MatrixKey&) = default; };
struct MatrixKeyHash { std::size_t operator()(const MatrixKey& k) const noexcept { return k.state ^ (k.opcode<<1) ^ (k.selector<<2); } };
struct MatrixCell { Identity cell_id{}; Identity function_id{}; Identity regime_id{}; Identity guard_set_id{}; Identity sentinel_set_id{}; Identity success_cell_id{}; Identity failure_cell_id{}; Identity recovery_cell_id{}; Mask flags{}; };
class ExecutionMatrix {
public:
    void bind(MatrixKey key, MatrixCell cell) { cells_[key] = cell; }
    std::optional<MatrixCell> lookup(MatrixKey key) const { auto it=cells_.find(key); if(it==cells_.end()) return std::nullopt; return it->second; }
private:
    std::unordered_map<MatrixKey,MatrixCell,MatrixKeyHash> cells_;
};
}
