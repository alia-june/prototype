"""Seeded data generators. No product calls define expected results."""
import base64
import copy
import random

from ..models import Block, Properties, Snapshot, Style, text_digest
from ..rich import CellText, RichBlock, Snapshot2, Span, TableCell, TableRow
from .core import CASE_SCHEMA


def case(kind, data, seed):
    return {"schema":CASE_SCHEMA,"kind":kind,"seed":seed,"input":data}


def snapshot(rng, rich=False):
    props=Properties(font_family="Arial")
    cls=RichBlock if rich else Block
    blocks=[]
    for index in range(rng.randint(2,7)):
        text=rng.choice(["Plain text","café e\u0301","Line\nnext","RTL العربية","Emoji 🙂","<escaped> & text"])+str(index)
        attrs={"block_id":f"b{index}","text":text,"style":Style(bold=rng.choice([True,False,None]))}
        if rich:
            attrs["runs"]=(Span(text=text,style=Style(italic=rng.choice([True,None]),font_family=rng.choice([None,"Times New Roman"]))),)
        blocks.append(cls(**attrs))
    if rich:
        cell=TableCell(paragraphs=(CellText(runs=(Span(text="Cell",style=Style(font_family="Consolas")),)),))
        blocks.append(RichBlock(block_id="table",kind="table",rows=(TableRow(cells=(cell,cell),header=True),TableRow(cells=(cell,cell)))))
    return (Snapshot2 if rich else Snapshot)(properties=props,blocks=tuple(blocks))


def batch_case(rng, seed, rich=False, invalid=False):
    source=snapshot(rng,rich)
    active=[b.block_id for b in source.blocks]
    originals=set(active)
    texts={b.block_id:b.text for b in source.blocks}
    operations=[]
    for index in range(rng.randint(1,55)):
        kind=rng.choice(["font","style","property","restore","insert","remove","move","text"])
        op={"operation_id":f"op{index}"}
        if kind=="font":
            op.update(kind="set_font",font_family=rng.choice(["Arial","Consolas","Times New Roman"]))
        elif kind=="style" and active:
            prop=rng.choice(["font_family","bold","italic","font_size_mpt"])
            values={"font_family":[None,"Arial","Consolas"],"bold":[True,False,None],"italic":[True,False,None],"font_size_mpt":[11000,14000,None]}
            op.update(kind="set_style",targets=[rng.choice(active)],property=prop,value=rng.choice(values[prop]))
        elif kind=="restore" and set(active).issubset(originals):
            op.update(kind="restore_font")
        elif kind=="insert":
            ident=f"new{index}"
            text="Inserted "+str(index)
            block=(RichBlock if rich else Block)(block_id=ident,text=text)
            after=rng.choice([None,*active])
            active.insert(0 if after is None else active.index(after)+1,ident)
            texts[ident]=text
            op.update(kind="insert_block",block=block.model_dump(mode="json"),after=after)
        elif kind=="remove" and len(active)>1:
            target=rng.choice(active)
            active.remove(target)
            op.update(kind="remove_block",target=target)
        elif kind=="move" and active:
            target=rng.choice(active)
            active.remove(target)
            after=rng.choice([None,*active])
            active.insert(0 if after is None else active.index(after)+1,target)
            op.update(kind="move_block",target=target,after=after)
        elif kind=="text" and active and not rich:
            target=rng.choice(active)
            text="Changed "+str(index)
            op.update(kind="replace_text",target=target,text=text,expected_text_sha256=text_digest(texts[target]))
            texts[target]=text
        else:
            op.update(kind="set_property",property="title",value="Case "+str(index))
        operations.append(op)
    expected=None
    if invalid:
        # Independent invalid first request: later operations cannot hide it.
        operations.insert(0,{"operation_id":"invalid-first","kind":"set_style","targets":["absent"],"property":"bold","value":True})
        expected="UNKNOWN_TARGET"
    return case("batch",{"snapshot":source.model_dump(mode="json"),"batch":{"base_sha256":source.digest,"operations":operations},"expected_error":expected},seed)


def generate(seed, count=500):
    rng=random.Random(seed)
    for index in range(count):
        category=index%8
        if category<3:
            value=batch_case(rng,seed,rich=category==1,invalid=category==2)
        elif category==3:
            text=rng.choice(["alpha","café","e\u0301","العربية","🙂"])+str(index)
            choices=[("# "+text+"\n\n**bold** and *italic*.",text+"\n"+"="*(len(text)+2)+"\n\n__bold__ and _italic_."),
                     ("- "+text+"\n- second", "* "+text+"\n* second"),
                     ("A [link](https://example.com/)","A [link][reference]\n\n[reference]: https://example.com/")]
            left,right=rng.choice(choices)
            value=case("markdown_pair",{"left":left,"right":right},seed)
        elif category in (4,5):
            text=rng.choice(["Plain café e\u0301", "Line one\nLine two", "A\tB", "A\rB", "A\x00B", "Symbols <> &", "Emoji 🙂", "العربية"])
            if category==4:
                text=text.replace("\r"," ").replace("\x00"," ")
            bold=rng.choice([None,True])
            block=RichBlock(block_id="text",text=text,runs=(Span(text=text,style=Style(bold=bold,italic=rng.choice([None,True]))),))
            source=Snapshot2(properties=Properties(font_family="Arial"),blocks=(block,))
            data={"snapshot":source.model_dump(mode="json"),"allowed_losses":[]}
            if category==5 and "\x00" in text:
                data["expected_error"]="UNREPRESENTABLE_DOCX"
            elif category==5 and "\r" in text:
                data["allowed_losses"]=["DOCX_CARRIAGE_RETURN"]
            value=case("markdown_roundtrip" if category==4 else "docx_roundtrip",data,seed)
        elif category==6:
            requests=[{"request_key":"bad","text":True},{"request_key":"bad","text":"x","extra":"no"},
                      {"request_key":"bad","snapshot":{"properties":{"font_size_mpt":"11000"}}},
                      {"request_key":"bad","text":"x","title":False},
                      {"request_key":"bad","snapshot":{"blocks":[{"block_id":"same"},{"block_id":"same"}]}},
                      {"request_key":"bad","text":"\ud800"}]
            value=case("invalid_request",{"request":copy.deepcopy(rng.choice(requests)),"expected_error":"VALIDATION_ERROR"},seed)
        else:
            from ..format_common import deterministic_zip
            variants=[b"not a ZIP",b"PK\x03\x04broken",deterministic_zip({"../escape.xml":b"x"}),
                      deterministic_zip({"word/document.xml":b'<!DOCTYPE a><a/>'}),
                      deterministic_zip({"Word/document.xml":b"x","word/document.xml":b"y"})]
            raw=rng.choice(variants)
            value=case("malformed_package",{"data_base64":base64.b64encode(raw).decode(),"expected_errors":["INVALID_PACKAGE","INVALID_XML"]},seed)
        yield value
