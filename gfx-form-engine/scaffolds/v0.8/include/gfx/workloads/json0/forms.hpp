#pragma once
#include <gfx/workloads/json0/parser.hpp>
#include <vector>

namespace gfx::json0 {
enum class FormKind : Code { Document=1, Object=2, Array=3, Member=4, Primitive=5 };
struct FormInstance {
    Identity form_id{};
    FormKind kind{FormKind::Primitive};
    Identity node_id{};
    Identity source_span_id{};
    Identity parent_node_id{};
    Value depth{};
};
inline std::vector<FormInstance> recognize_forms(const JsonDocument& document) {
    std::vector<FormInstance> out; Identity id=1;
    for(const auto& n:document.nodes) {
        FormKind kind=FormKind::Primitive;
        switch(n.node_type) {
            case NodeType::Document: kind=FormKind::Document; break;
            case NodeType::Object: kind=FormKind::Object; break;
            case NodeType::Array: kind=FormKind::Array; break;
            case NodeType::Member: kind=FormKind::Member; break;
            case NodeType::Value: kind=FormKind::Primitive; break;
        }
        out.push_back({id++,kind,n.node_id,n.source_span_id,n.parent_node_id,n.depth});
    }
    return out;
}
}
