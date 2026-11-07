#pragma once
#include <gfx/structures/frame.hpp>
#include <gfx/molecular/relation.hpp>
#include <vector>
namespace gfx {
enum class FrameRelationKind : Code { EmbeddedIn=1, ProjectsTo=2, TransformsTo=3, AlignsWith=4, DerivedFrom=5 };
struct FrameRelation { Identity relation_id{}; Identity source_frame_id{}; FrameRelationKind kind{FrameRelationKind::AlignsWith}; Identity target_frame_id{}; Identity mapping_id{}; };
class FrameGraph {
public:
 void add(FrameRelation r){ relations_.push_back(r); }
 const std::vector<FrameRelation>& relations() const noexcept { return relations_; }
private: std::vector<FrameRelation> relations_;
};
}
