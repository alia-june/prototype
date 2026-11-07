#pragma once
#include <gfx/atomic/types.hpp>
#include <array>
#include <bitset>
#include <optional>
#include <stdexcept>
namespace gfx {
template<class T, std::size_t Edge>
class Brick {
public:
    static constexpr std::size_t voxel_count = Edge*Edge*Edge;
    static constexpr std::size_t index(std::size_t x,std::size_t y,std::size_t z) { return x + Edge*(y + Edge*z); }
    void set(std::size_t x,std::size_t y,std::size_t z,T value) { auto i=index(x,y,z); if(i>=voxel_count) throw std::out_of_range("brick"); values_[i]=std::move(value); occupied_.set(i); }
    std::optional<T> get(std::size_t x,std::size_t y,std::size_t z) const { auto i=index(x,y,z); if(i>=voxel_count || !occupied_.test(i)) return std::nullopt; return values_[i]; }
    const std::bitset<voxel_count>& occupancy() const noexcept { return occupied_; }
private:
    std::array<T,voxel_count> values_{};
    std::bitset<voxel_count> occupied_{};
};
}
