#pragma once
#include <gfx/atomic/types.hpp>
#include <gfx/molecular/reference.hpp>
namespace gfx {
struct Validation {
    Identity validation_id{};
    Identity subject_reference_id{};
    Code check_code{};
    Code result_code{};
    Identity evidence_reference_id{};
};
}
