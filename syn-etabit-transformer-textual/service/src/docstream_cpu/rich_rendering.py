"""Escaped HTML for version-two structures; no executable source markup."""
import base64
from html import escape

from .assets import validate_references
from .errors import ModelError
from .models import Style
from .rich import Span

CSS = """table{border-collapse:collapse;width:100%;margin:12pt 0 18pt;table-layout:fixed}td,th{border:1px solid #d9d9d9;padding:7pt;vertical-align:middle;overflow-wrap:anywhere}th{background:#edf1f5;text-align:left}td p,th p{margin:0 0 5pt}td p:last-child,th p:last-child{margin-bottom:0}img{max-width:100%;height:auto;display:block;margin:10pt 0 16pt}a{color:inherit;text-decoration:underline}code{background:#f2f5f8}li>ul,li>ol{margin-bottom:0}"""


def build(snapshot, profile, aliases, get_asset):
    if get_asset is None and any(b.kind=="image" for b in snapshot.blocks):
        raise ModelError("ASSET_UNAVAILABLE", "renderer requires managed image bytes")
    validate_references(snapshot,get_asset)

    def css(style, base=None, code=False):
        parent = base or Style()
        # Version two null fonts inherit the document default even for code.
        # A presentation-only code font must not defeat an all-text assignment.
        family = style.font_family or parent.font_family or snapshot.properties.font_family
        result = ["font-family:"+aliases[family]]
        for name, prop in (("font_size_mpt","font-size"),("bold","font-weight"),("italic","font-style")):
            value = getattr(style,name)
            if value is None:
                value = getattr(parent,name)
            if value is not None:
                text = str(value/1000)+"pt" if name=="font_size_mpt" else ("bold" if value else "normal") if name=="bold" else ("italic" if value else "normal")
                result.append(prop+":"+text)
        return ";".join(result)

    def spans(runs, parent, code=False):
        parts = []
        for run in runs:
            tag = "code" if run.code else "span"
            text = f'<{tag} data-ds-text style="{css(run.style,parent,code or run.code)}">{escape(run.text)}</{tag}>'
            if run.href:
                text = f'<a href="{escape(run.href,quote=True)}" rel="noreferrer">{text}</a>'
            parts.append(text)
        return "".join(parts)

    parts, stack, open_items = [], [], []

    def close_lists(depth=-1):
        while len(stack)>depth+1:
            if open_items.pop():
                parts.append("</li>")
            parts.append("</"+stack.pop()+">")

    for index,b in enumerate(snapshot.blocks):
        if b.kind=="list_item":
            depth=b.list_depth
            tag="ol" if b.list_kind=="ordered" else "ul"
            close_lists(depth)
            if len(stack)>depth and stack[depth]!=tag:
                close_lists(depth-1)
            if len(stack)==depth:
                parts.append(f'<{tag}'+(f' start="{b.list_start}"' if tag=="ol" else "")+">")
                stack.append(tag)
                open_items.append(False)
            if open_items[depth]:
                parts.append("</li>")
            parts.append(f'<li id="ds-{index}" style="{css(b.style)}">'+spans(b.runs or (Span(text=b.text),),b.style))
            open_items[depth]=True
            continue
        close_lists()
        if b.kind=="table":
            parts.append("<table>")
            for row in b.rows:
                parts.append("<tr>")
                for cell in row.cells:
                    tag="th" if row.header else "td"
                    parts.append("<"+tag+">")
                    for paragraph in cell.paragraphs:
                        parts.append("<p>"+spans(paragraph.runs,b.style)+"</p>")
                    parts.append("</"+tag+">")
                parts.append("</tr>")
            parts.append("</table>")
        elif b.kind=="image":
            image=b.image
            encoded=base64.b64encode(get_asset(image.sha256)).decode()
            parts.append(f'<img src="data:{image.media_type};base64,{encoded}" alt="{escape(image.alt,quote=True)}" style="width:{image.width_mpt/1000}pt;height:{image.height_mpt/1000}pt;max-width:100%;object-fit:contain">')
        else:
            tag="h"+str(b.heading_level) if b.kind=="heading" else "pre" if b.kind=="code" else "p"
            parts.append(f'<{tag} id="ds-{index}" style="{css(b.style,code=b.kind=="code")}">'+spans(b.runs or (Span(text=b.text),),b.style,b.kind=="code")+f'</{tag}>')
    close_lists()
    return "".join(parts)
