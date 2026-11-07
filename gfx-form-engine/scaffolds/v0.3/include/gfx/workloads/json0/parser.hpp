#pragma once
#include <gfx/workloads/json0/lexical.hpp>
#include <gfx/workloads/json0/model.hpp>
#include <string_view>
#include <vector>
#include <string>
namespace gfx::json0 {
enum class ParseErrorCode : Code { None=0, Utf8=1, Syntax=2, Number=3, Literal=4, String=5, Trailing=6, Structure=7 };
struct ParseError { ParseErrorCode code{ParseErrorCode::None}; Offset offset{}; std::string message; };
struct JsonDocument {
    Identity source_id{}; Generation generation{}; Json0Result lexical;
    std::vector<SourceSpan> spans; std::vector<DataElement> data;
    std::vector<StructureNode> nodes; std::vector<SequenceElement> sequence;
    std::vector<ParseError> errors;
    [[nodiscard]] bool valid() const noexcept { return errors.empty() && lexical.strings_balanced && lexical.structure_balanced; }
};
bool validate_utf8(std::string_view source, Offset* bad_offset=nullptr) noexcept;
bool validate_number(std::string_view token) noexcept;
JsonDocument parse(std::string_view source, Identity source_id=1, Generation generation=1);
}
