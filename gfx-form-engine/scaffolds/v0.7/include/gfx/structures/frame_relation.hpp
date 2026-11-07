#pragma once
#include <gfx/structures/frame.hpp>
#include <gfx/molecular/relation.hpp>
#include <algorithm>
#include <optional>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace gfx {
enum class FrameRelationKind : Code { EmbeddedIn=1, ProjectsTo=2, TransformsTo=3, AlignsWith=4, DerivedFrom=5 };
struct FrameRelation { Identity relation_id{}; Identity source_frame_id{}; FrameRelationKind kind{FrameRelationKind::AlignsWith}; Identity target_frame_id{}; Identity mapping_id{}; };
class FrameGraph {
public:
    void add(FrameRelation r){ relations_.push_back(r); }
    const std::vector<FrameRelation>& relations() const noexcept { return relations_; }

    std::optional<std::vector<FrameRelation>> path(Identity source, Identity target) const {
        if (source==target) return std::vector<FrameRelation>{};
        struct Parent { Identity previous{}; const FrameRelation* edge{}; };
        std::queue<Identity> q; std::unordered_set<Identity> seen; std::unordered_map<Identity,Parent> parent;
        q.push(source); seen.insert(source);
        while(!q.empty()) {
            auto current=q.front(); q.pop();
            for (const auto& edge:relations_) {
                if (edge.source_frame_id!=current || seen.count(edge.target_frame_id)) continue;
                seen.insert(edge.target_frame_id); parent[edge.target_frame_id]={current,&edge};
                if (edge.target_frame_id==target) {
                    std::vector<FrameRelation> out; Identity n=target;
                    while(n!=source) { auto it=parent.find(n); if(it==parent.end()) return std::nullopt; out.push_back(*it->second.edge); n=it->second.previous; }
                    std::reverse(out.begin(),out.end()); return out;
                }
                q.push(edge.target_frame_id);
            }
        }
        return std::nullopt;
    }
private: std::vector<FrameRelation> relations_;
};
}
