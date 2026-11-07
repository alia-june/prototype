#include <gfx/workloads/json0/fragments.hpp>
#include <gfx/workloads/json0/forms.hpp>
#include <cassert>
#include <string>
int main(){
    const std::string source=R"({"a":[true,null]})";
    auto doc=gfx::json0::parse(source,4,3); assert(doc.valid());
    auto t=gfx::json0::literal_fragment(1,"true",3); auto n=gfx::json0::literal_fragment(2,"null",3);
    auto pt=source.find("true"), pn=source.find("null"); assert(pt!=std::string::npos && pn!=std::string::npos);
    assert(gfx::json0::match_fragment(t,source,doc.lexical.elr,pt)); assert(gfx::json0::match_fragment(n,source,doc.lexical.elr,pn));
    auto forms=gfx::json0::recognize_forms(doc); bool member=false,array=false; for(const auto& f:forms){member|=f.kind==gfx::json0::FormKind::Member;array|=f.kind==gfx::json0::FormKind::Array;} assert(member&&array);
}
