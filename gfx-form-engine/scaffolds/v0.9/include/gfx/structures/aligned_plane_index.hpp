#pragma once
#include <gfx/structures/aligned_planes.hpp>
#include <unordered_map>

namespace gfx {
struct AlignedPlaneEntry {
    Coordinate coordinate{};
    std::optional<DirectionIntent> direction;
    std::optional<PossibilitySet> possibilities;
    std::optional<RecoverySet> recovery;
};

class AlignedPlaneIndex {
public:
    AlignedPlaneIndex(Identity frame_id, Generation generation, Value validation_epoch)
        : frame_id_(frame_id), generation_(generation), validation_epoch_(validation_epoch) {}

    bool build(const Plane<DirectionIntent>& p1, const Plane<PossibilitySet>& p2, const Plane<RecoverySet>& p3,
               const std::vector<Coordinate>& coordinates) {
        if (p1.frame_id()!=frame_id_ || p2.frame_id()!=frame_id_ || p3.frame_id()!=frame_id_) return false;
        if (p1.generation()!=generation_ || p2.generation()!=generation_ || p3.generation()!=generation_) return false;
        entries_.clear();
        for (const auto& coordinate : coordinates)
            entries_[coordinate] = {coordinate,p1.get(coordinate),p2.get(coordinate),p3.get(coordinate)};
        return true;
    }

    [[nodiscard]] const AlignedPlaneEntry* get(Coordinate coordinate) const noexcept {
        const auto it=entries_.find(coordinate); return it==entries_.end()?nullptr:&it->second;
    }
    [[nodiscard]] Identity frame_id() const noexcept { return frame_id_; }
    [[nodiscard]] Generation generation() const noexcept { return generation_; }
    [[nodiscard]] Value validation_epoch() const noexcept { return validation_epoch_; }
    [[nodiscard]] std::size_t size() const noexcept { return entries_.size(); }

private:
    Identity frame_id_{};
    Generation generation_{};
    Value validation_epoch_{};
    std::unordered_map<Coordinate,AlignedPlaneEntry,CoordinateHash> entries_;
};
}
