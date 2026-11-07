#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace gfx {

using Digest256 = std::array<std::uint8_t, 32>;

Digest256 sha256(std::span<const std::byte> bytes) noexcept;
Digest256 sha256(std::string_view text) noexcept;
std::string digest_hex(const Digest256& digest);
bool digest_is_zero(const Digest256& digest) noexcept;

inline bool operator==(const Digest256& a, const Digest256& b) noexcept {
    for (std::size_t i=0;i<a.size();++i) if (a[i]!=b[i]) return false;
    return true;
}
inline bool operator!=(const Digest256& a, const Digest256& b) noexcept { return !(a==b); }

void append_u64_be(std::vector<std::byte>& out, std::uint64_t value);
void append_digest(std::vector<std::byte>& out, const Digest256& digest);

}
