#include <gfx/runtime/integrity.hpp>
#include <array>
#include <iomanip>
#include <sstream>

namespace gfx {
namespace {
constexpr std::array<std::uint32_t,64> k{
0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u};

constexpr std::uint32_t rotr(std::uint32_t x, std::uint32_t n) noexcept { return (x>>n)|(x<<(32u-n)); }
}

Digest256 sha256(std::span<const std::byte> bytes) noexcept {
    std::array<std::uint32_t,8> h{0x6a09e667u,0xbb67ae85u,0x3c6ef372u,0xa54ff53au,0x510e527fu,0x9b05688cu,0x1f83d9abu,0x5be0cd19u};
    std::vector<std::uint8_t> msg; msg.reserve(bytes.size()+72);
    for (auto b:bytes) msg.push_back(std::to_integer<std::uint8_t>(b));
    const std::uint64_t bit_len=static_cast<std::uint64_t>(msg.size())*8u;
    msg.push_back(0x80u);
    while ((msg.size()%64u)!=56u) msg.push_back(0u);
    for (int i=7;i>=0;--i) msg.push_back(static_cast<std::uint8_t>((bit_len>>(i*8))&0xffu));

    std::array<std::uint32_t,64> w{};
    for (std::size_t chunk=0;chunk<msg.size();chunk+=64) {
        for (std::size_t i=0;i<16;++i) {
            const std::size_t j=chunk+i*4;
            w[i]=(static_cast<std::uint32_t>(msg[j])<<24)|(static_cast<std::uint32_t>(msg[j+1])<<16)|
                 (static_cast<std::uint32_t>(msg[j+2])<<8)|static_cast<std::uint32_t>(msg[j+3]);
        }
        for (std::size_t i=16;i<64;++i) {
            const auto s0=rotr(w[i-15],7)^rotr(w[i-15],18)^(w[i-15]>>3);
            const auto s1=rotr(w[i-2],17)^rotr(w[i-2],19)^(w[i-2]>>10);
            w[i]=w[i-16]+s0+w[i-7]+s1;
        }
        auto a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
        for (std::size_t i=0;i<64;++i) {
            const auto S1=rotr(e,6)^rotr(e,11)^rotr(e,25);
            const auto ch=(e&f)^((~e)&g);
            const auto temp1=hh+S1+ch+k[i]+w[i];
            const auto S0=rotr(a,2)^rotr(a,13)^rotr(a,22);
            const auto maj=(a&b)^(a&c)^(b&c);
            const auto temp2=S0+maj;
            hh=g; g=f; f=e; e=d+temp1; d=c; c=b; b=a; a=temp1+temp2;
        }
        h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e; h[5]+=f; h[6]+=g; h[7]+=hh;
    }
    Digest256 out{};
    for (std::size_t i=0;i<8;++i) {
        out[i*4]=static_cast<std::uint8_t>(h[i]>>24);
        out[i*4+1]=static_cast<std::uint8_t>(h[i]>>16);
        out[i*4+2]=static_cast<std::uint8_t>(h[i]>>8);
        out[i*4+3]=static_cast<std::uint8_t>(h[i]);
    }
    return out;
}

Digest256 sha256(std::string_view text) noexcept {
    return sha256(std::span<const std::byte>(reinterpret_cast<const std::byte*>(text.data()),text.size()));
}

std::string digest_hex(const Digest256& digest) {
    std::ostringstream out; out<<std::hex<<std::setfill('0');
    for (auto b:digest) out<<std::setw(2)<<static_cast<unsigned>(b);
    return out.str();
}

bool digest_is_zero(const Digest256& digest) noexcept {
    for (auto b:digest) if (b!=0) return false;
    return true;
}

void append_u64_be(std::vector<std::byte>& out, std::uint64_t value) {
    for (int i=7;i>=0;--i) out.push_back(static_cast<std::byte>((value>>(i*8))&0xffu));
}
void append_digest(std::vector<std::byte>& out, const Digest256& digest) {
    for (auto b:digest) out.push_back(static_cast<std::byte>(b));
}

}
