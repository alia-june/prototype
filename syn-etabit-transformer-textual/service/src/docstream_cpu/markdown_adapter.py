"""Declared CommonMark 0.31.2 subset with the markdown-it table extension."""
from dataclasses import replace
from hashlib import sha256
import json
import re

from markdown_it import MarkdownIt

from .assets import validate_image
from .errors import ModelError
from .format_common import Losses, deterministic_zip, safe_asset_name
from .models import Properties, Style
from .rich import CellText, ImageRef, RichBlock, Snapshot2, Span, TableCell, TableRow, safe_link


def merge_runs(runs):
    result = []
    for run in runs:
        if not run.text:
            continue
        if result and result[-1].style == run.style and result[-1].code == run.code and result[-1].href == run.href:
            result[-1] = Span(**{**run.model_dump(), "text": result[-1].text + run.text})
        else:
            result.append(run)
    return tuple(result)


def inline(tokens, losses, location):
    runs, bold, italic, link = [], 0, 0, None
    for token in tokens:
        kind = token.type
        if kind in ("strong_open", "em_open"):
            bold += int(kind == "strong_open")
            italic += int(kind == "em_open")
        elif kind in ("strong_close", "em_close"):
            bold -= int(kind == "strong_close")
            italic -= int(kind == "em_close")
        elif kind == "link_open":
            href = token.attrGet("href")
            if safe_link(href):
                link = href
            else:
                losses.add("LINK_TARGET", location, "unsupported link target retained as text")
            if token.attrGet("title"):
                losses.add("LINK_TITLE", location, "link title is unsupported")
        elif kind == "link_close":
            link = None
        else:
            text = token.content
            if kind == "softbreak":
                text = " "
            elif kind == "hardbreak":
                text = "\n"
            elif kind not in ("text", "code_inline"):
                losses.add("INLINE_" + kind.upper(), location, "unsupported inline feature represented as literal text")
            runs.append(Span(text=text, style=Style(bold=True if bold else None, italic=True if italic else None), code=kind == "code_inline", href=link))
    return merge_runs(runs)


def import_markdown(raw, assets, *, properties=None, image_metadata=None):
    losses = Losses()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ModelError("UNSUPPORTED_ENCODING", "Markdown requires UTF-8") from exc
    # Parse HTML tokens so unsupported constructs are reported instead of executed.
    tokens = MarkdownIt("commonmark", {"html": True, "maxNesting": 32}).enable("table").parse(text)
    blocks, images, lists, items = [], {}, [], []

    def add(kind, **kwargs):
        block = RichBlock(block_id=f"b{len(blocks)+1}", kind=kind, **kwargs)
        blocks.append(block)

    i = 0
    while i < len(tokens):
        token = tokens[i]
        location = f"line:{token.map[0]+1}" if token.map else f"token:{i}"
        kind = token.type
        if kind in ("bullet_list_open", "ordered_list_open"):
            lists.append(("ordered" if kind == "ordered_list_open" else "bullet", int(token.attrGet("start") or 1)))
        elif kind in ("bullet_list_close", "ordered_list_close"):
            lists.pop()
        elif kind == "list_item_open":
            items.append(0)
        elif kind == "list_item_close":
            items.pop()
        elif kind in ("paragraph_open", "heading_open"):
            node = tokens[i+1]
            children = node.children or []
            if lists:
                if items[-1]:
                    losses.add("LIST_MULTI_PARAGRAPH", location, "multiple paragraphs in a list item become separate items")
                items[-1] += 1
            if len(children) == 1 and children[0].type == "image" and not lists:
                image = children[0]
                name = image.attrGet("src")
                if name not in assets or not safe_asset_name(name):
                    losses.add("IMAGE_SOURCE", location, "image requires an explicitly supplied local PNG/JPEG asset")
                    add("paragraph", text=image.content)
                else:
                    content = assets[name]
                    media, width, height = validate_image(content)
                    content_hash = sha256(content).hexdigest()
                    images[content_hash] = content
                    sizing = (image_metadata or {}).get(content_hash, {})
                    add("image", image=ImageRef(sha256=content_hash, media_type=media, alt=image.content,
                        width_mpt=sizing.get("width_mpt", min(width*750, 468000)),
                        height_mpt=sizing.get("height_mpt", max(1, round(height*min(width*750,468000)/width)))))
                    if image.attrGet("title"):
                        losses.add("IMAGE_TITLE", location, "image title is unsupported")
            else:
                runs = inline(children, losses, location)
                attrs = {"text": "".join(r.text for r in runs), "runs": runs}
                if lists:
                    if len(lists) > 9:
                        raise ModelError("LIST_LIMIT", "list depth exceeds eight")
                    add("list_item", list_kind=lists[-1][0], list_depth=len(lists)-1, list_start=lists[-1][1], **attrs)
                elif kind == "heading_open":
                    add("heading", heading_level=int(token.tag[1:]), **attrs)
                else:
                    add("paragraph", **attrs)
            i += 2
        elif kind in ("fence", "code_block"):
            if token.info:
                losses.add("CODE_LANGUAGE", location, "code language metadata is unsupported")
            if lists:
                losses.add("LIST_CODE", location, "code container in a list becomes a standalone block")
            add("code", text=token.content)
        elif kind == "table_open":
            rows, cells, header = [], [], False
            i += 1
            while tokens[i].type != "table_close":
                part = tokens[i]
                if part.type == "thead_open":
                    header = True
                elif part.type == "thead_close":
                    header = False
                elif part.type == "tr_open":
                    cells = []
                elif part.type in ("th_open", "td_open"):
                    if part.attrGet("style"):
                        losses.add("TABLE_ALIGNMENT", location, "column alignment is unsupported")
                    runs = inline(tokens[i+1].children or [], losses, location)
                    cells.append(TableCell(paragraphs=(CellText(runs=runs),)))
                elif part.type == "tr_close":
                    rows.append(TableRow(cells=tuple(cells), header=header))
                i += 1
            if lists:
                losses.add("LIST_TABLE", location, "nested table becomes a standalone block")
            add("table", rows=tuple(rows))
        elif kind in ("blockquote_open", "blockquote_close"):
            if kind == "blockquote_open":
                losses.add("BLOCK_QUOTE", location, "quotation container is flattened")
        elif kind in ("html_block", "hr"):
            losses.add("BLOCK_" + kind.upper(), location, "unsupported block represented as literal text")
            add("paragraph", text=token.content or "---")
        elif kind.endswith("_close"):
            pass
        else:
            losses.add("BLOCK_" + kind.upper(), location, "unsupported block")
        i += 1
    props = properties or Properties(font_family="Arial")
    return Snapshot2(properties=props, blocks=tuple(blocks)), images, losses


def escape_md(text):
    return re.sub(r"([\\`*_{}\[\]()#+.!>|~\-])", r"\\\1", text)


def export_markdown(snapshot, get_asset):
    losses, parts, entries, image_metadata = Losses(), [], {}, {}

    def spans(runs, location, block_style=None):
        output = []
        for run in runs:
            style = run.style
            if style.font_family is not None or style.font_size_mpt is not None or style.bold is False or style.italic is False:
                losses.add("MARKDOWN_RUN_STYLE", location, "Markdown cannot represent font or explicit inheritance overrides")
            text = escape_md(run.text).replace("\n", "  \n")
            if run.code:
                fence = "`" * (max([len(x) for x in re.findall(r"`+", run.text)] or [0]) + 1)
                text = fence + " " + run.text + " " + fence
            bold = style.bold if style.bold is not None else (block_style.bold if block_style else None)
            italic = style.italic if style.italic is not None else (block_style.italic if block_style else None)
            if bold:
                text = "**" + text + "**"
            if italic:
                text = "*" + text + "*"
            if run.href:
                # Angle brackets delimit URLs, whose brackets/backslashes must be encoded.
                href = run.href.replace("<", "%3C").replace(">", "%3E").replace(" ", "%20")
                text = f"[{text}](<{href}>)"
            output.append(text)
        return "".join(output)

    for b in snapshot.blocks:
        location = "block:" + b.block_id
        if b.style.font_family is not None or b.style.font_size_mpt is not None:
            losses.add("MARKDOWN_BLOCK_STYLE", location, "Markdown cannot represent block font settings")
        runs = getattr(b, "runs", ()) or (Span(text=b.text),)
        body = spans(runs, location, b.style)
        if b.kind == "heading":
            parts.append("#"*b.heading_level + " " + body)
        elif b.kind == "code":
            fence = "`" * max(3, max([len(x) for x in re.findall(r"`+", b.text)] or [0]) + 1)
            if getattr(b, "runs", ()) or any(v is not None for v in b.style.model_dump().values()):
                losses.add("MARKDOWN_CODE_STYLE", location, "code-block formatting is unsupported")
            parts.append(fence + "\n" + b.text + ("" if b.text.endswith("\n") else "\n") + fence)
            if not b.text.endswith("\n"):
                losses.add("CODE_FINAL_NEWLINE", location, "fenced code requires a final newline")
        elif b.kind == "list_item":
            marker = str(getattr(b, "list_start", 1)) + ". " if b.list_kind == "ordered" else "- "
            parts.append("    "*getattr(b, "list_depth", 0) + marker + body.replace("\n", "\n" + "    "*(getattr(b, "list_depth", 0)+1)))
        elif b.kind == "table":
            rows = list(b.rows)
            if not rows[0].header:
                losses.add("TABLE_HEADER_REQUIRED", location, "Markdown requires a header; an empty header is inserted")
                empty = TableCell(paragraphs=(CellText(),))
                rows.insert(0, TableRow(cells=(empty,)*len(rows[0].cells), header=True))
            if any(r.header for r in rows[1:]):
                losses.add("TABLE_HEADER_POSITION", location, "only the first row can be a Markdown header")
            lines = []
            for index, row in enumerate(rows):
                values = []
                for cell in row.cells:
                    if len(cell.paragraphs) != 1 or any("\n" in r.text for p in cell.paragraphs for r in p.runs):
                        losses.add("TABLE_CELL_PARAGRAPHS", location, "cell paragraphs and line breaks become spaces")
                    values.append(" ".join(spans(p.runs, location, b.style).replace("\n", " ") for p in cell.paragraphs))
                lines.append("| " + " | ".join(values) + " |")
                if index == 0:
                    lines.append("| " + " | ".join("---" for _ in row.cells) + " |")
            parts.append("\n".join(lines))
        elif b.kind == "image":
            image = b.image
            suffix = ".png" if image.media_type == "image/png" else ".jpg"
            name = "assets/" + image.sha256 + suffix
            entries[name] = get_asset(image.sha256)
            image_metadata[image.sha256] = {"width_mpt": image.width_mpt, "height_mpt": image.height_mpt}
            parts.append(f"![{escape_md(image.alt)}]({name})")
        else:
            if not body:
                losses.add("EMPTY_PARAGRAPH", location, "Markdown drops empty paragraphs")
            parts.append(body)
    # Preserve properties and image dimensions in the explicit Docstream bundle.
    entries["document.md"] = ("\n\n".join(parts) + "\n").encode()
    entries["docstream.json"] = json.dumps({"schema": "docstream.markdown-bundle/1", "properties": snapshot.properties.model_dump(), "images": image_metadata}, ensure_ascii=False, sort_keys=True).encode()
    # Parse emitted Markdown as an independent syntax check. Delimiter edge
    # cases must not silently change meaning, even when an emitter looks valid.
    reparsed, _, report = import_markdown(entries["document.md"], entries, properties=snapshot.properties, image_metadata=image_metadata)
    def meaning(s):
        def runs(values, text="", style=Style()):
            values = values or (Span(text=text),)
            normalized = []
            for value in values:
                item = (value.text, bool(value.style.bold if value.style.bold is not None else style.bold), bool(value.style.italic if value.style.italic is not None else style.italic), value.code, value.href)
                if normalized and normalized[-1][1:]==item[1:]:
                    normalized[-1]=(normalized[-1][0]+item[0], *item[1:])
                else:
                    normalized.append(item)
            return normalized
        result=[]
        for b in s.blocks:
            value=[b.kind,b.text,b.heading_level,b.list_kind,getattr(b,"list_depth",0),getattr(b,"list_start",1),runs(getattr(b,"runs",()),b.text,b.style)]
            if b.kind=="table":
                value.append([(r.header,[[runs(p.runs,style=b.style) for p in c.paragraphs] for c in r.cells]) for r in b.rows])
            if b.kind=="image":
                value.append(b.image.model_dump())
            result.append(value)
        return result
    if report.items or meaning(snapshot)!=meaning(reparsed):
        losses.add("MARKDOWN_ROUNDTRIP", "document", "emitted Markdown does not preserve every supported semantic detail; inspect output before accepting loss")
    return deterministic_zip(entries), losses
