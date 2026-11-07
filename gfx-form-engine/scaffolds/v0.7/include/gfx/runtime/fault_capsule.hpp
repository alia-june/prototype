#pragma once
#include <gfx/runtime/breadcrumb.hpp>
#include <gfx/runtime/recovery.hpp>
namespace gfx {
struct FaultCapsule {
    Identity fault_id{};
    Breadcrumb breadcrumb{};
    Identity recovery_domain_id{};
    Identity recovery_set_id{};
    Code failure_code{};
    Mask sentinel_failed{};
    Generation last_committed_generation{};
};
}
