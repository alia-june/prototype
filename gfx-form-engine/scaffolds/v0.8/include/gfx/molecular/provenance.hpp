#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx {
struct Provenance {
    Identity provenance_id{};
    Identity subject_reference_id{};
    Identity source_reference_id{};
    Identity operation_id{};
    Generation generation{};
    Identity authority_id{};
};
}
