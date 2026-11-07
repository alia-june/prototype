#include <gfx/molecular/recursion.hpp>
namespace gfx {
RecursionDisposition govern_recursion(const RecursionInvariantSet& i) noexcept {
    return i.permits_continue() ? RecursionDisposition::Continue : RecursionDisposition::EnterRecoveryPlane;
}
}
