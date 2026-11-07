#pragma once
#include <gfx/atomic/types.hpp>
#include <optional>
#include <unordered_map>
#include <utility>

namespace gfx {
template<class T>
class HomogeneousBackingPool {
public:
    bool insert(Identity id, T value) {
        return entries_.emplace(id, std::move(value)).second;
    }
    T* find(Identity id) {
        auto it = entries_.find(id); return it == entries_.end() ? nullptr : &it->second;
    }
    const T* find(Identity id) const {
        auto it = entries_.find(id); return it == entries_.end() ? nullptr : &it->second;
    }
    bool erase(Identity id) { return entries_.erase(id) != 0; }
    std::size_t size() const noexcept { return entries_.size(); }
private:
    std::unordered_map<Identity,T> entries_;
};
}
