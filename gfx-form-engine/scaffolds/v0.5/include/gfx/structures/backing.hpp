#pragma once
#include <gfx/atomic/types.hpp>
#include <vector>
#include <unordered_map>
#include <optional>

namespace gfx {
enum class BackingClass : Code { Dense=1, Sparse=2, Brick=3, Cpu=4, Gpu=5 };
struct BackingBinding { BackingClass backing_class{BackingClass::Dense}; Identity backing_id{}; };

template<class T>
class DenseBacking {
public:
    explicit DenseBacking(std::size_t n = 0) : data_(n) {}
    T& at(std::size_t i) { return data_.at(i); }
    const T& at(std::size_t i) const { return data_.at(i); }
    std::size_t size() const noexcept { return data_.size(); }
private:
    std::vector<T> data_;
};

template<class Key, class T>
class SparseBacking {
public:
    void set(const Key& k, T v) { data_[k] = std::move(v); }
    std::optional<T> get(const Key& k) const {
        auto it = data_.find(k); if (it == data_.end()) return std::nullopt; return it->second;
    }
private:
    std::unordered_map<Key,T> data_;
};
}
