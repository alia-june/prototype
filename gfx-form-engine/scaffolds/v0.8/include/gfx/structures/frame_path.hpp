#pragma once
#include <gfx/structures/frame_relation.hpp>
#include <gfx/structures/frame_mapping.hpp>
#include <optional>
#include <unordered_map>

namespace gfx {
class FrameMappingRegistry {
public:
    bool insert(FrameTransformBinding binding) { return mappings_.emplace(binding.mapping_id,std::move(binding)).second; }
    const FrameTransformBinding* find(Identity mapping_id) const {
        auto it=mappings_.find(mapping_id); return it==mappings_.end()?nullptr:&it->second;
    }
private:
    std::unordered_map<Identity,FrameTransformBinding> mappings_;
};
inline std::optional<CoordinateAddress> map_frame_path(CoordinateAddress address,
                                                       const std::vector<FrameRelation>& path,
                                                       const FrameMappingRegistry& registry) {
    for(const auto& edge:path) {
        if(edge.source_frame_id!=address.frame_id || edge.mapping_id==0) return std::nullopt;
        const auto* binding=registry.find(edge.mapping_id);
        if(!binding || binding->source_frame_id!=edge.source_frame_id || binding->destination_frame_id!=edge.target_frame_id) return std::nullopt;
        auto next=map_address(address,*binding); if(!next) return std::nullopt; address=*next;
    }
    return address;
}
}
