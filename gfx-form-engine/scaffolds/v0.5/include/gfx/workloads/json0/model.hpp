#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/molecular/relation.hpp>
#include <vector>
namespace gfx::json0 {
enum class ValueClass : Code { String=1, Number=2, True=3, False=4, Null=5, Object=6, Array=7, Unknown=8 };
enum class NodeType : Code { Document=1, Object=2, Array=3, Member=4, Value=5 };
struct SourceSpan { Identity span_id{}; Identity source_id{}; Offset offset{}; Length length{}; };
struct DataElement { Identity data_id{}; Identity source_span_id{}; ValueClass value_class{ValueClass::Unknown}; Identity owning_node_id{}; Mask flags{}; };
struct StructureNode { Identity node_id{}; NodeType node_type{NodeType::Value}; Identity source_span_id{}; Identity parent_node_id{}; Identity first_child_node_id{}; Identity next_sibling_node_id{}; Value depth{}; Identity opening_structure_id{}; Identity closing_structure_id{}; };
enum class SemanticOrder : Code { None=0, Required=1 };
enum class JsonRelationCode : Code { Contains=1, NextSibling=2 };
struct SequenceElement { Identity sequence_id{}; Identity subject_id{}; Sequence source_ordinal{}; Identity previous_id{}; Identity next_id{}; SemanticOrder semantic_order{SemanticOrder::None}; };
}
