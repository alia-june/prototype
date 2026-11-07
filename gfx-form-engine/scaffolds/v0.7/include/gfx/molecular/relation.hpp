#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
struct Relation {
    Identity relation_id{};
    Identity source_id{};
    Code relation_code{};
    Identity target_id{};
    Code state{};
};
}
