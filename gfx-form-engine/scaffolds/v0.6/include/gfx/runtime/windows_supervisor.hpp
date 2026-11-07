#pragma once
#include <gfx/atomic/types.hpp>
namespace gfx::runtime {
// Contract scaffold only. Intended implementation uses Windows Job Objects,
// shared mappings and event handles. No OS behavior is claimed here.
struct WorkerHeartbeat { Identity worker_instance_id{}; Generation active_generation{}; TransactionId last_received{}; TransactionId last_completed{}; Code current_opcode{}; Code queue_state{}; Mask sentinel_summary{}; };
class WindowsGpuSupervisor {
public:
    virtual ~WindowsGpuSupervisor() = default;
    virtual bool launch_worker() = 0;
    virtual bool terminate_worker() = 0;
    virtual bool accept_heartbeat(const WorkerHeartbeat&) = 0;
};
}
