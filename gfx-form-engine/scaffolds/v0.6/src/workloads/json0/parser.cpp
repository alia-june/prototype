#include <gfx/workloads/json0/parser.hpp>
#include <algorithm>
#include <cctype>
#include <string_view>

namespace gfx::json0 {

bool validate_utf8(std::string_view s, Offset* bad) noexcept {
    std::size_t i = 0;
    while (i < s.size()) {
        const auto c = static_cast<unsigned char>(s[i]);
        if (c < 0x80) { ++i; continue; }
        std::size_t n = 0; std::uint32_t cp = 0;
        if ((c & 0xE0) == 0xC0) { n = 2; cp = c & 0x1F; if (cp < 2) { if (bad) *bad=i; return false; } }
        else if ((c & 0xF0) == 0xE0) { n = 3; cp = c & 0x0F; }
        else if ((c & 0xF8) == 0xF0) { n = 4; cp = c & 0x07; if (cp > 4) { if (bad) *bad=i; return false; } }
        else { if (bad) *bad=i; return false; }
        if (i+n > s.size()) { if (bad) *bad=i; return false; }
        for (std::size_t j=1;j<n;++j) {
            const auto d=static_cast<unsigned char>(s[i+j]);
            if ((d&0xC0)!=0x80) { if (bad) *bad=i+j; return false; }
            cp=(cp<<6)|(d&0x3F);
        }
        if ((n==3&&cp<0x800)||(n==4&&cp<0x10000)||(cp>=0xD800&&cp<=0xDFFF)||cp>0x10FFFF) { if (bad) *bad=i; return false; }
        i+=n;
    }
    return true;
}

bool validate_number(std::string_view t) noexcept {
    if (t.empty()) return false;
    std::size_t i=0;
    if (t[i]=='-') { if (++i==t.size()) return false; }
    if (t[i]=='0') ++i;
    else {
        if (i>=t.size() || !std::isdigit(static_cast<unsigned char>(t[i]))) return false;
        while (i<t.size() && std::isdigit(static_cast<unsigned char>(t[i]))) ++i;
    }
    if (i<t.size() && t[i]=='.') {
        if (++i==t.size() || !std::isdigit(static_cast<unsigned char>(t[i]))) return false;
        while (i<t.size() && std::isdigit(static_cast<unsigned char>(t[i]))) ++i;
    }
    if (i<t.size() && (t[i]=='e'||t[i]=='E')) {
        ++i;
        if (i<t.size() && (t[i]=='+'||t[i]=='-')) ++i;
        if (i==t.size() || !std::isdigit(static_cast<unsigned char>(t[i]))) return false;
        while (i<t.size() && std::isdigit(static_cast<unsigned char>(t[i]))) ++i;
    }
    return i==t.size();
}

namespace {
enum class TokKind { LBrace,RBrace,LBracket,RBracket,Colon,Comma,String,Number,True,False,Null,End,Invalid };
struct Tok { TokKind kind{TokKind::Invalid}; std::size_t a{},b{}; };
inline int hex_digit(unsigned char c) noexcept {
    if(c>='0'&&c<='9') return c-'0';
    if(c>='a'&&c<='f') return 10+(c-'a');
    if(c>='A'&&c<='F') return 10+(c-'A');
    return -1;
}
struct Lexer {
    std::string_view s; std::size_t i{}; ParseError* err{};
    void ws(){ while(i<s.size() && (s[i]==' '||s[i]=='\t'||s[i]=='\r'||s[i]=='\n')) ++i; }
    bool read_hex4(std::uint16_t& out) {
        if(i+4>s.size()) return false;
        std::uint16_t v=0;
        for(int k=0;k<4;++k) { const int h=hex_digit(static_cast<unsigned char>(s[i+k])); if(h<0) return false; v=static_cast<std::uint16_t>((v<<4)|h); }
        i+=4; out=v; return true;
    }
    Tok next(){
        ws(); if(i>=s.size()) return {TokKind::End,i,i}; const std::size_t a=i; const char c=s[i++];
        switch(c){
            case '{':return{TokKind::LBrace,a,i}; case '}':return{TokKind::RBrace,a,i};
            case '[':return{TokKind::LBracket,a,i}; case ']':return{TokKind::RBracket,a,i};
            case ':':return{TokKind::Colon,a,i}; case ',':return{TokKind::Comma,a,i};
            case '"': {
                while(i<s.size()) {
                    const unsigned char q=static_cast<unsigned char>(s[i++]);
                    if(q=='"') return {TokKind::String,a,i};
                    if(q<0x20) { if(err)*err={ParseErrorCode::String,(Offset)(i-1),"control in string"}; return{TokKind::Invalid,a,i}; }
                    if(q!='\\') continue;
                    if(i>=s.size()) { if(err)*err={ParseErrorCode::String,(Offset)i,"truncated escape"}; return{TokKind::Invalid,a,i}; }
                    const char e=s[i++];
                    if(e=='u') {
                        const auto first_offset=i;
                        std::uint16_t u1{};
                        if(!read_hex4(u1)) { if(err)*err={ParseErrorCode::String,(Offset)first_offset,"invalid unicode escape"}; return{TokKind::Invalid,a,i}; }
                        if(u1>=0xD800 && u1<=0xDBFF) {
                            if(i+2>s.size() || s[i]!='\\' || s[i+1]!='u') { if(err)*err={ParseErrorCode::String,(Offset)i,"high surrogate without low surrogate"}; return{TokKind::Invalid,a,i}; }
                            i+=2; const auto second_offset=i; std::uint16_t u2{};
                            if(!read_hex4(u2) || u2<0xDC00 || u2>0xDFFF) { if(err)*err={ParseErrorCode::String,(Offset)second_offset,"invalid low surrogate"}; return{TokKind::Invalid,a,i}; }
                        } else if(u1>=0xDC00 && u1<=0xDFFF) {
                            if(err) *err={ParseErrorCode::String,(Offset)first_offset,"lone low surrogate"};
                            return {TokKind::Invalid,a,i};
                        }
                    } else if(std::string_view("\"\\/bfnrt").find(e)==std::string_view::npos) {
                        if(err) *err={ParseErrorCode::String,(Offset)(i-1),"invalid escape"};
                        return {TokKind::Invalid,a,i};
                    }
                }
                if(err)*err={ParseErrorCode::String,(Offset)a,"unclosed string"};
                return {TokKind::Invalid,a,i};
            }
            default: break;
        }
        --i;
        if(s.substr(i,4)=="true"){i+=4;return{TokKind::True,a,i};}
        if(s.substr(i,5)=="false"){i+=5;return{TokKind::False,a,i};}
        if(s.substr(i,4)=="null"){i+=4;return{TokKind::Null,a,i};}
        while(i<s.size() && !std::isspace(static_cast<unsigned char>(s[i])) && std::string_view(",]}:").find(s[i])==std::string_view::npos) ++i;
        if(i>a && validate_number(s.substr(a,i-a))) return{TokKind::Number,a,i};
        if(err)*err={ParseErrorCode::Syntax,(Offset)a,"invalid token"};
        return {TokKind::Invalid,a,i};
    }
};
enum class CtxKind { Document,Object,Array };
enum class Expect { Value, Done, ObjectKeyOrEnd, ObjectColon, ObjectValue, ObjectCommaOrEnd, ArrayValueOrEnd, ArrayCommaOrEnd };
struct Ctx { CtxKind kind{CtxKind::Document}; Identity node{}; Value depth{}; Expect expect{Expect::Value}; Identity current_member{}; Identity last_sequence_subject{}; std::size_t open_offset{}; };
}


bool validate_relationships(const JsonDocument& document) noexcept {
    for (const auto& node : document.nodes) {
        if (node.parent_node_id) {
            bool found=false;
            for (const auto& r:document.relations) if (r.source_id==node.parent_node_id && r.target_id==node.node_id && r.relation_code==static_cast<Code>(JsonRelationCode::Contains)) { found=true; break; }
            if (!found) return false;
        }
        if (node.next_sibling_node_id) {
            bool found=false;
            for (const auto& r:document.relations) if (r.source_id==node.node_id && r.target_id==node.next_sibling_node_id && r.relation_code==static_cast<Code>(JsonRelationCode::NextSibling)) { found=true; break; }
            if (!found) return false;
        }
        if (node.node_type==NodeType::Member) {
            bool key=false, value=false;
            for (const auto& r:document.relations) {
                if(r.source_id!=node.node_id) continue;
                if(r.relation_code==static_cast<Code>(JsonRelationCode::MemberKey)) key=true;
                if(r.relation_code==static_cast<Code>(JsonRelationCode::MemberValue)) value=true;
            }
            if(!key || !value) return false;
        }
    }
    return true;
}

bool validate_sequence(const JsonDocument& document) noexcept {
    for (const auto& e:document.sequence) {
        if (e.next_id) {
            bool back=false;
            for (const auto& n:document.sequence) if (n.subject_id==e.next_id && n.previous_id==e.subject_id) { back=true; break; }
            if (!back) return false;
        }
        if (e.previous_id) {
            bool forward=false;
            for (const auto& p:document.sequence) if (p.subject_id==e.previous_id && p.next_id==e.subject_id) { forward=true; break; }
            if (!forward) return false;
        }
    }
    return true;
}

JsonDocument parse(std::string_view source, Identity sid, Generation gen) {
    JsonDocument d; d.source_id=sid; d.generation=gen; d.lexical=build_elr(source,sid,gen);
    Offset bad{}; if(!validate_utf8(source,&bad)){d.errors.push_back({ParseErrorCode::Utf8,bad,"invalid UTF-8"});return d;}
    Identity next_id=1; Sequence next_sequence=1;
    auto make_span=[&](std::size_t a,std::size_t b){Identity id=next_id++;d.spans.push_back({id,sid,(Offset)a,(Length)(b-a)});return id;};
    auto find_node=[&](Identity id)->StructureNode*{for(auto&n:d.nodes)if(n.node_id==id)return &n;return nullptr;};
    auto add_node=[&](NodeType type,Identity parent,Identity span,Value depth){Identity id=next_id++;d.nodes.push_back({id,type,span,parent,0,0,depth,0,0}); if(parent){auto*p=find_node(parent); if(p){if(!p->first_child_node_id)p->first_child_node_id=id;else{Identity cur=p->first_child_node_id;while(auto*c=find_node(cur)){if(!c->next_sibling_node_id){c->next_sibling_node_id=id;break;}cur=c->next_sibling_node_id;}}}}return id;};
    auto add_sequence=[&](Ctx& c,Identity subject,SemanticOrder order){d.sequence.push_back({next_id++,subject,next_sequence++,c.last_sequence_subject,0,order}); if(c.last_sequence_subject){for(auto&se:d.sequence)if(se.subject_id==c.last_sequence_subject){se.next_id=subject;break;}}c.last_sequence_subject=subject;};
    const Identity doc=add_node(NodeType::Document,0,0,0); std::vector<Ctx> stack{{CtxKind::Document,doc,0,Expect::Value,0,0,0}};
    ParseError lexerr; Lexer lx{source,0,&lexerr};
    auto syntax=[&](const Tok&t,const char*m){d.errors.push_back({ParseErrorCode::Syntax,(Offset)t.a,m});};
    bool finished=false;
    while(!finished && d.errors.empty()){
        Tok t=lx.next(); if(t.kind==TokKind::Invalid){d.errors.push_back(lexerr);break;} if(stack.empty()){syntax(t,"internal parser stack empty");break;} Ctx& c=stack.back();
        auto parent_for_value=[&](){return c.kind==CtxKind::Object?c.current_member:c.node;};
        auto value_complete=[&](Identity subject){
            if(c.kind==CtxKind::Document){c.expect=Expect::Done;}
            else if(c.kind==CtxKind::Object){add_sequence(c,c.current_member,SemanticOrder::None);c.current_member=0;c.expect=Expect::ObjectCommaOrEnd;}
            else {add_sequence(c,subject,SemanticOrder::Required);c.expect=Expect::ArrayCommaOrEnd;}
        };
        auto primitive=[&](ValueClass vc){Identity sp=make_span(t.a,t.b);Identity n=add_node(NodeType::Value,parent_for_value(),sp,c.depth+1);d.data.push_back({next_id++,sp,vc,n,0});value_complete(n);};
        if(c.expect==Expect::Done){ if(t.kind==TokKind::End){finished=true;break;} syntax(t,"trailing content"); break; }
        if(c.kind==CtxKind::Object && c.expect==Expect::ObjectKeyOrEnd){ if(t.kind==TokKind::RBrace){const auto closed_node=c.node; const auto open=c.open_offset; auto*n=find_node(closed_node);if(n)n->source_span_id=make_span(open,t.b);stack.pop_back();if(stack.empty()){finished=true;break;}Ctx& p=stack.back(); if(p.kind==CtxKind::Document)p.expect=Expect::Done; else if(p.kind==CtxKind::Object){add_sequence(p,p.current_member,SemanticOrder::None);p.current_member=0;p.expect=Expect::ObjectCommaOrEnd;} else {add_sequence(p,closed_node,SemanticOrder::Required);p.expect=Expect::ArrayCommaOrEnd;} continue;} if(t.kind!=TokKind::String){syntax(t,"expected object key or close");break;}Identity ksp=make_span(t.a,t.b);Identity mem=add_node(NodeType::Member,c.node,0,c.depth+1);d.data.push_back({next_id++,ksp,ValueClass::String,mem,0});c.current_member=mem;c.expect=Expect::ObjectColon;continue; }
        if(c.kind==CtxKind::Object && c.expect==Expect::ObjectColon){if(t.kind!=TokKind::Colon){syntax(t,"expected colon");break;}c.expect=Expect::ObjectValue;continue;}
        if(c.kind==CtxKind::Object && c.expect==Expect::ObjectCommaOrEnd){if(t.kind==TokKind::Comma){c.expect=Expect::ObjectKeyOrEnd;continue;}if(t.kind==TokKind::RBrace){auto closing=t; auto node=c.node; auto open=c.open_offset; stack.pop_back();auto*n=find_node(node);if(n)n->source_span_id=make_span(open,closing.b);if(stack.empty()){finished=true;break;}Ctx&p=stack.back(); if(p.kind==CtxKind::Document)p.expect=Expect::Done;else if(p.kind==CtxKind::Object){add_sequence(p,p.current_member,SemanticOrder::None);p.current_member=0;p.expect=Expect::ObjectCommaOrEnd;}else{add_sequence(p,node,SemanticOrder::Required);p.expect=Expect::ArrayCommaOrEnd;}continue;}syntax(t,"expected comma or object close");break;}
        if(c.kind==CtxKind::Array && c.expect==Expect::ArrayValueOrEnd && t.kind==TokKind::RBracket){auto node=c.node;auto open=c.open_offset;stack.pop_back();auto*n=find_node(node);if(n)n->source_span_id=make_span(open,t.b);if(stack.empty()){finished=true;break;}Ctx&p=stack.back();if(p.kind==CtxKind::Document)p.expect=Expect::Done;else if(p.kind==CtxKind::Object){add_sequence(p,p.current_member,SemanticOrder::None);p.current_member=0;p.expect=Expect::ObjectCommaOrEnd;}else{add_sequence(p,node,SemanticOrder::Required);p.expect=Expect::ArrayCommaOrEnd;}continue;}
        if(c.kind==CtxKind::Array && c.expect==Expect::ArrayCommaOrEnd){if(t.kind==TokKind::Comma){c.expect=Expect::ArrayValueOrEnd;continue;}if(t.kind==TokKind::RBracket){auto node=c.node;auto open=c.open_offset;stack.pop_back();auto*n=find_node(node);if(n)n->source_span_id=make_span(open,t.b);if(stack.empty()){finished=true;break;}Ctx&p=stack.back();if(p.kind==CtxKind::Document)p.expect=Expect::Done;else if(p.kind==CtxKind::Object){add_sequence(p,p.current_member,SemanticOrder::None);p.current_member=0;p.expect=Expect::ObjectCommaOrEnd;}else{add_sequence(p,node,SemanticOrder::Required);p.expect=Expect::ArrayCommaOrEnd;}continue;}syntax(t,"expected comma or array close");break;}
        const bool expects_value = c.expect==Expect::Value || c.expect==Expect::ObjectValue || c.expect==Expect::ArrayValueOrEnd;
        if(!expects_value){syntax(t,"unexpected parser state");break;}
        if(t.kind==TokKind::LBrace){Identity n=add_node(NodeType::Object,parent_for_value(),0,c.depth+1); if(c.kind==CtxKind::Document)c.expect=Expect::Done; else if(c.kind==CtxKind::Object)c.expect=Expect::ObjectCommaOrEnd; else c.expect=Expect::ArrayCommaOrEnd; stack.push_back({CtxKind::Object,n,c.depth+1,Expect::ObjectKeyOrEnd,0,0,t.a});continue;}
        if(t.kind==TokKind::LBracket){Identity n=add_node(NodeType::Array,parent_for_value(),0,c.depth+1); if(c.kind==CtxKind::Document)c.expect=Expect::Done; else if(c.kind==CtxKind::Object)c.expect=Expect::ObjectCommaOrEnd; else c.expect=Expect::ArrayCommaOrEnd; stack.push_back({CtxKind::Array,n,c.depth+1,Expect::ArrayValueOrEnd,0,0,t.a});continue;}
        switch(t.kind){case TokKind::String:primitive(ValueClass::String);break;case TokKind::Number:primitive(ValueClass::Number);break;case TokKind::True:primitive(ValueClass::True);break;case TokKind::False:primitive(ValueClass::False);break;case TokKind::Null:primitive(ValueClass::Null);break;case TokKind::End:syntax(t,"expected value");break;default:syntax(t,"expected value");break;}
    }
    Tok tail=lx.next(); if(d.errors.empty() && !finished && tail.kind!=TokKind::End) d.errors.push_back({ParseErrorCode::Trailing,(Offset)tail.a,"trailing content"});
    if(d.errors.empty() && !stack.empty() && !(stack.size()==1 && stack.front().expect==Expect::Done)) d.errors.push_back({ParseErrorCode::Structure,(Offset)source.size(),"incomplete structure"});
    if(!d.lexical.strings_balanced && d.errors.empty()) d.errors.push_back({ParseErrorCode::String,(Offset)source.size(),"unbalanced string"});
    if(!d.lexical.structure_balanced && d.errors.empty()) d.errors.push_back({ParseErrorCode::Structure,(Offset)source.size(),"unbalanced structure"});
    if(auto*n=find_node(doc);n && !n->source_span_id)n->source_span_id=make_span(0,source.size());
    auto find_span=[&](Identity id)->const SourceSpan*{for(const auto& sp:d.spans) if(sp.span_id==id) return &sp; return nullptr;};
    for(auto& n:d.nodes) {
        if(n.node_type!=NodeType::Member) continue;
        const DataElement* key=nullptr; for(const auto& de:d.data) if(de.owning_node_id==n.node_id && de.value_class==ValueClass::String){key=&de;break;}
        const StructureNode* value=nullptr; if(n.first_child_node_id) for(const auto& candidate:d.nodes) if(candidate.node_id==n.first_child_node_id){value=&candidate;break;}
        if(key && value) {
            const auto* ksp=find_span(key->source_span_id); const auto* vsp=find_span(value->source_span_id);
            if(ksp && vsp) n.source_span_id=make_span(static_cast<std::size_t>(ksp->offset),static_cast<std::size_t>(vsp->offset+vsp->length));
            d.relations.push_back({next_id++,n.node_id,static_cast<Code>(JsonRelationCode::MemberKey),key->data_id,0});
            d.relations.push_back({next_id++,n.node_id,static_cast<Code>(JsonRelationCode::MemberValue),value->node_id,0});
        }
    }
    for (const auto& n:d.nodes) {
        if (n.parent_node_id) d.relations.push_back({next_id++,n.parent_node_id,static_cast<Code>(JsonRelationCode::Contains),n.node_id,0});
        if (n.next_sibling_node_id) d.relations.push_back({next_id++,n.node_id,static_cast<Code>(JsonRelationCode::NextSibling),n.next_sibling_node_id,0});
    }
    if (d.errors.empty() && !validate_relationships(d)) d.errors.push_back({ParseErrorCode::Structure,0,"relationship validation failed"});
    if (d.errors.empty() && !validate_sequence(d)) d.errors.push_back({ParseErrorCode::Structure,0,"sequence validation failed"});
    return d;
}
}
