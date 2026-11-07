#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
struct Coordinate { std::int64_t x{}, y{}, z{}; friend bool operator==(const Coordinate&, const Coordinate&) = default; };
struct CoordinateAddress {
    Identity frame_id{};
    Coordinate coordinate{};
    Generation generation{};
    friend bool operator==(const CoordinateAddress&, const CoordinateAddress&) = default;
};
struct Direction { std::int64_t dx{}, dy{}, dz{}; };
inline Coordinate step(Coordinate c, Direction d) { return {c.x+d.dx, c.y+d.dy, c.z+d.dz}; }
}
