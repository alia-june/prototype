#pragma once
#include <gfx/atomic/types.hpp>
#include <unordered_map>
#include <optional>
namespace gfx {
class GenerationRegistry {
public:
    void publish(Identity subject, Generation generation) { current_[subject]=generation; }
    std::optional<Generation> current(Identity subject) const { auto it=current_.find(subject); if(it==current_.end()) return std::nullopt; return it->second; }
    bool matches(Identity subject, Generation generation) const { auto g=current(subject); return g && *g==generation; }
private:
    std::unordered_map<Identity,Generation> current_;
};
}
