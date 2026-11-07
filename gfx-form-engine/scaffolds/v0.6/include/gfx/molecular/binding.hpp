#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
struct Binding {
    Identity binding_id{};
    Identity subject_id{};
    Code role{};
    Identity object_id{};
    Value inline_value{};
    bool uses_inline_value{false};
};
}
