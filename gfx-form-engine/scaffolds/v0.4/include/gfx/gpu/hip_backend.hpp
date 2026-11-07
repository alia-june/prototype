#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx::gpu {
// Scaffold only. HIP runtime integration intentionally remains behind this boundary
// until validated on the Windows 11 + RX 7700 XT target.
struct HipCapabilities {
    bool runtime_available{false};
    bool pinned_host_memory{false};
    bool mapped_host_memory{false};
    bool async_copy{false};
    Value vram_bytes{};
};
class HipBackend {
public:
    HipCapabilities probe() const { return {}; }
};
}
