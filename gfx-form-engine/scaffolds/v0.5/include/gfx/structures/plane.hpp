#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/structures/coordinate.hpp>
#include <gfx/structures/backing.hpp>
#include <gfx/structures/plane_descriptor.hpp>
#include <optional>
#include <unordered_map>

namespace gfx {
struct CoordinateHash {
    std::size_t operator()(const Coordinate& c) const noexcept {
        auto h1 = std::hash<std::int64_t>{}(c.x);
        auto h2 = std::hash<std::int64_t>{}(c.y);
        auto h3 = std::hash<std::int64_t>{}(c.z);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }
};

template<class T>
class Plane {
public:
    Plane(Identity plane_id, Identity frame_id, Generation generation,
          BackingBinding backing={BackingClass::Sparse,0})
      : plane_id_(plane_id), frame_id_(frame_id), generation_(generation), backing_(backing) {}
    void set(Coordinate c, T value) { cells_[c] = std::move(value); }
    std::optional<T> get(Coordinate c) const {
        auto it = cells_.find(c); if (it == cells_.end()) return std::nullopt; return it->second;
    }
    Identity plane_id() const noexcept { return plane_id_; }
    Identity frame_id() const noexcept { return frame_id_; }
    Generation generation() const noexcept { return generation_; }
    std::size_t size() const noexcept { return cells_.size(); }
    PlaneDescriptor descriptor(Value element_width_bits=sizeof(T)*8) const noexcept {
        return {plane_id_,frame_id_,generation_,backing_,static_cast<Length>(cells_.size()),element_width_bits,0};
    }
private:
    Identity plane_id_{};
    Identity frame_id_{};
    Generation generation_{};
    BackingBinding backing_{};
    std::unordered_map<Coordinate,T,CoordinateHash> cells_;
};
}
