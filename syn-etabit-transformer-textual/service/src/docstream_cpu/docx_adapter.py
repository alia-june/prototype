"""Conservative DOCX mapping with bounded package preflight and explicit losses."""
from hashlib import sha256
from io import BytesIO
import re

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from .assets import validate_image
from .errors import ModelError
from .format_common import Losses, deterministic_zip, read_package, xml
from .markdown_adapter import merge_runs
from .models import Properties, Style
from .rich import CellText, ImageRef, RichBlock, Snapshot2, Span, TableCell, TableRow, safe_link

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W, "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships", "a": "http://schemas.openxmlformats.org/drawingml/2006/main", "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}


def el(tag, **attrs):
    node = OxmlElement(tag)
    for name, value in attrs.items():
        node.set(qn(name), str(value))
    return node


def style_chain(style):
    seen = set()
    while style is not None and style.style_id not in seen:
        seen.add(style.style_id)
        yield style
        style = style.base_style


def inherited(style, prop):
    for item in style_chain(style):
        value = getattr(item.font, prop)
        if value is not None:
            return value
    return None


def theme_name(font, theme):
    rpr = font._element.find(qn("w:rPr"))
    fonts = rpr.find(qn("w:rFonts")) if rpr is not None else None
    if fonts is not None:
        value = fonts.get(qn("w:asciiTheme")) or fonts.get(qn("w:hAnsiTheme"))
        if value:
            return theme.get("major" if value.startswith("major") else "minor")
    return None


def font_style(font, inherited_from=None, theme=None):
    values = {}
    for name, prop in (("font_family", "name"), ("font_size_mpt", "size"), ("bold", "bold"), ("italic", "italic")):
        value = getattr(font, prop)
        if prop == "name" and value is None:
            value = theme_name(font, theme or {})
        if value is None and inherited_from is not None:
            if prop == "name":
                value = next((s.font.name or theme_name(s.font, theme or {}) for s in style_chain(inherited_from) if s.font.name or theme_name(s.font, theme or {})), None)
            else:
                value = inherited(inherited_from, prop)
        values[name] = int(round(value.pt*1000)) if prop == "size" and value is not None else value
    return Style(**values)


def import_docx(raw):
    package = read_package(raw)
    losses = Losses()
    if "word/document.xml" not in package:
        raise ModelError("INVALID_DOCX", "package has no main Word document")
    # Every XML part is preflighted before the document library opens the package.
    for name, content in package.items():
        if name.endswith((".xml", ".rels")):
            tree = xml(content)
            if name.endswith(".rels"):
                for relation in tree:
                    if relation.get("TargetMode") == "External":
                        if not relation.get("Type", "").endswith("/hyperlink") or not safe_link(relation.get("Target", "")):
                            losses.add("EXTERNAL_RELATIONSHIP", name, "external relationship is unsupported and never fetched")
        if any(marker in name.lower() for marker in ("vbaproject", "embeddings/", "activex/", "comments", "footnotes", "endnotes", "header", "footer")):
            losses.add("PACKAGE_FEATURE", name, "package feature is outside the supported document body")
    tree = xml(package["word/document.xml"])
    for tag, code in (("ins", "TRACKED_CHANGE"), ("del", "TRACKED_CHANGE"), ("fldChar", "FIELD"), ("fldSimple", "FIELD"),
                      ("sdt", "CONTENT_CONTROL"), ("altChunk", "ALTERNATE_CONTENT"), ("vMerge", "MERGED_CELL"), ("gridSpan", "MERGED_CELL")):
        if tree.findall(".//w:"+tag, NS):
            losses.add(code, "word/document.xml", tag + " is unsupported")
    if tree.findall(".//wp:anchor", NS):
        losses.add("FLOATING_IMAGE", "word/document.xml", "floating images are unsupported")
    # Foreign vocabularies such as equations, VML and charts cannot disappear silently.
    known_ns = {W, NS["a"], NS["wp"], "http://schemas.openxmlformats.org/drawingml/2006/picture"}
    for node in tree.iter():
        if not isinstance(node.tag,str):
            continue
        namespace = node.tag.split("}")[0][1:] if "}" in node.tag else ""
        if namespace not in known_ns:
            losses.add("XML_VOCABULARY", "word/document.xml", "unsupported vocabulary " + namespace)
    try:
        doc = Document(BytesIO(raw))
    except Exception as exc:
        raise ModelError("INVALID_DOCX", "document library could not open the package") from exc
    normal = doc.styles["Normal"]
    theme = {}
    if "word/theme/theme1.xml" in package:
        theme_xml = xml(package["word/theme/theme1.xml"])
        for name in ("major", "minor"):
            node = theme_xml.find(".//a:"+name+"Font/a:latin", NS)
            if node is not None and node.get("typeface"):
                theme[name] = node.get("typeface")
    normal_style = font_style(normal.font, normal.base_style, theme)
    defaults = doc.styles.element.find(qn("w:docDefaults"))
    default_rpr = defaults.find(".//"+qn("w:rPr")) if defaults is not None else None
    default_fonts = default_rpr.find(qn("w:rFonts")) if default_rpr is not None else None
    default_family = None
    if default_fonts is not None:
        default_family = default_fonts.get(qn("w:ascii")) or theme.get("major" if default_fonts.get(qn("w:asciiTheme"),"").startswith("major") else "minor")
    family = normal_style.font_family or default_family
    if family is None:
        raise ModelError("UNRESOLVED_FONT", "document default font cannot be resolved from explicit styles or theme")
    size = inherited(normal, "size")
    default_size = default_rpr.find(qn("w:sz")) if default_rpr is not None else None
    section = doc.sections[0]
    properties = Properties(title=doc.core_properties.title or "", font_family=family,
        font_size_mpt=round(size.pt*1000) if size else int(default_size.get(qn("w:val")))*500 if default_size is not None else 11000,
        page_width_mpt=round(section.page_width.pt*1000), page_height_mpt=round(section.page_height.pt*1000))
    if len(doc.sections) != 1:
        losses.add("SECTIONS", "word/document.xml", "only the first page dimensions are retained")
    # Model has no section margins, headers, columns or paragraph placement controls.
    for s in doc.sections:
        if any(round(getattr(s, p).pt*1000) != 72000 for p in ("top_margin", "bottom_margin", "left_margin", "right_margin")):
            losses.add("SECTION_MARGINS", "word/document.xml", "section margins are not represented")
    blocks, assets = [], {}
    numbering = doc.part.numbering_part.element

    def location(paragraph):
        return "body:" + str(len(blocks)+1)

    def paragraph_runs(paragraph, cell=False):
        result = []
        loc = location(paragraph)
        # Inspect the styles actually used by this paragraph, including inherited
        # font effects; unused template styles do not imply document losses.
        for style in style_chain(paragraph.style):
            rpr = style.element.find(qn("w:rPr"))
            if rpr is not None:
                for prop in rpr:
                    tag = prop.tag.split("}")[-1]
                    if tag == "color" and prop.get(qn("w:val"),"auto").lower() not in ("auto","000000"):
                        losses.add("STYLE_COLOR", loc, "paragraph style color is outside the supported font model")
                    elif tag in ("u","strike","dstrike","highlight","vertAlign","smallCaps","caps","spacing","vanish"):
                        losses.add("STYLE_FONT_EFFECT", loc, "unsupported style font effect " + tag)
        for child in paragraph._p:
            if child.tag == qn("w:pPr"):
                continue
            href = None
            nodes = [child]
            if child.tag == qn("w:hyperlink"):
                rid = child.get(qn("r:id"))
                relation = paragraph.part.rels.get(rid)
                href = relation.target_ref if relation and relation.is_external else None
                if href is None or not safe_link(href):
                    losses.add("LINK_TARGET", loc, "unsupported hyperlink target becomes text")
                    href = None
                nodes = list(child)
            elif child.tag != qn("w:r"):
                losses.add("PARAGRAPH_CONTENT", loc, "unsupported paragraph child " + child.tag.split("}")[-1])
                # Preserve readable text of rejected containers when loss is explicitly accepted.
                text = "".join(child.itertext())
                if text:
                    result.append(Span(text=text))
                continue
            for node in nodes:
                if node.tag != qn("w:r"):
                    losses.add("HYPERLINK_CONTENT", loc, "unsupported hyperlink child")
                    continue
                run = Run(node, paragraph)
                # Pictures are handled by the containing paragraph, not flattened here.
                for item in node:
                    tag = item.tag.split("}")[-1]
                    if tag not in ("rPr", "t", "tab", "br", "cr", "drawing", "lastRenderedPageBreak"):
                        losses.add("RUN_CONTENT", loc, "unsupported run child " + tag)
                    if tag == "br" and item.get(qn("w:type"), "textWrapping") != "textWrapping":
                        losses.add("PAGE_BREAK", loc, "page or column break becomes a line break")
                rpr = node.find(qn("w:rPr"))
                if rpr is not None:
                    supported = {"rStyle", "rFonts", "b", "i", "sz"}
                    for attr in rpr:
                        tag = attr.tag.split("}")[-1]
                        if tag not in supported:
                            losses.add("RUN_FORMAT", loc, "unsupported run formatting " + tag)
                charstyle = run.style if run.style.style_id != "DefaultParagraphFont" else None
                style = font_style(run.font, charstyle, theme)
                if charstyle is not None:
                    for inherited_style in style_chain(charstyle):
                        rpr = inherited_style.element.find(qn("w:rPr"))
                        if rpr is not None:
                            for prop in rpr:
                                tag = prop.tag.split("}")[-1]
                                if tag not in ("rFonts","b","i","sz","rStyle"):
                                    losses.add("CHARACTER_STYLE_EFFECT", loc, "unsupported character-style font effect " + tag)
                if cell:
                    paragraph_style = font_style(paragraph.style.font, paragraph.style.base_style, theme)
                    inherited_values = paragraph_style.model_dump()
                    if inherited_values["font_family"] == properties.font_family:
                        inherited_values["font_family"] = None
                    if inherited_values["font_size_mpt"] == properties.font_size_mpt:
                        inherited_values["font_size_mpt"] = None
                    style = Style(**{key:value if value is not None else inherited_values[key] for key,value in style.model_dump().items()})
                code = charstyle is not None and charstyle.style_id == "DocstreamInlineCode"
                result.append(Span(text=run.text, style=style, code=code, href=href))
        return merge_runs(result)

    def list_info(paragraph):
        numpr = paragraph._p.pPr.numPr if paragraph._p.pPr is not None else None
        if numpr is None:
            for style in style_chain(paragraph.style):
                if style.element.pPr is not None and style.element.pPr.numPr is not None:
                    numpr = style.element.pPr.numPr
                    break
        if numpr is None or numpr.numId is None or numpr.numId.val == 0:
            return None
        depth = numpr.ilvl.val if numpr.ilvl is not None else 0
        nums = numbering.xpath(f'./w:num[@w:numId="{numpr.numId.val}"]')
        if not nums:
            losses.add("NUMBERING", location(paragraph), "unresolved numbering definition")
            return ("bullet", min(depth, 8), 1)
        abstract_id = nums[0].find(qn("w:abstractNumId")).get(qn("w:val"))
        levels = numbering.xpath(f'./w:abstractNum[@w:abstractNumId="{abstract_id}"]/w:lvl[@w:ilvl="{depth}"]')
        if not levels:
            losses.add("NUMBERING", location(paragraph), "unresolved numbering level")
            return ("bullet", min(depth, 8), 1)
        level = levels[0]
        fmt = level.find(qn("w:numFmt")).get(qn("w:val"))
        if fmt not in ("bullet", "decimal") or depth > 8:
            losses.add("NUMBERING_FORMAT", location(paragraph), "numbering format or depth is unsupported")
        start_node = level.find(qn("w:start"))
        start = int(start_node.get(qn("w:val"))) if start_node is not None else 1
        override = nums[0].xpath(f'./w:lvlOverride[@w:ilvl="{depth}"]/w:startOverride')
        if override:
            start = int(override[0].get(qn("w:val")))
        return ("ordered" if fmt == "decimal" else "bullet", min(depth,8), start)

    for child in doc.element.body:
        ident = f"b{len(blocks)+1}"
        if child.tag == qn("w:p"):
            p = Paragraph(child, doc)
            runs = paragraph_runs(p)
            text = "".join(r.text for r in runs)
            pictures = child.xpath(".//wp:inline")
            if pictures:
                if len(pictures) != 1 or text:
                    losses.add("MIXED_IMAGE", location(p), "images must occupy their own paragraph; image/text are separated")
                    if text:
                        blocks.append(RichBlock(block_id=ident, text=text, runs=runs))
                        ident = f"b{len(blocks)+1}"
                for picture in pictures:
                    blips = picture.xpath(".//a:blip")
                    if not blips or not blips[0].get(qn("r:embed")):
                        losses.add("IMAGE_SOURCE", location(p), "image is not embedded")
                        continue
                    relation = doc.part.rels.get(blips[0].get(qn("r:embed")))
                    if relation is None or relation.is_external:
                        losses.add("IMAGE_SOURCE", location(p), "image relationship is unresolved or external")
                        continue
                    content = relation.target_part.blob
                    media, _, _ = validate_image(content)
                    content_hash = sha256(content).hexdigest()
                    assets[content_hash] = content
                    extent = picture.find(qn("wp:extent"))
                    desc = picture.find(qn("wp:docPr"))
                    blocks.append(RichBlock(block_id=f"b{len(blocks)+1}", kind="image", image=ImageRef(sha256=content_hash, media_type=media,
                        alt=desc.get("descr", "") if desc is not None else "",
                        width_mpt=max(1,round(int(extent.get("cx"))/12.7)), height_mpt=max(1,round(int(extent.get("cy"))/12.7)))))
                continue
            if p.style.style_id == "Title" and not blocks:
                if properties.title and properties.title != text:
                    losses.add("TITLE_CONFLICT", location(p), "title paragraph differs from title metadata; paragraph becomes the title")
                properties = Properties(**{**properties.model_dump(), "title": text})
                if any(r.href or r.code or any(v is not None for v in r.style.model_dump().values()) for r in runs):
                    losses.add("TITLE_FORMAT", location(p), "title text is retained as a property without inline formatting")
                continue
            attrs = {"text": text, "runs": runs, "style": font_style(p.style.font, p.style.base_style, theme)}
            style_ids = [s.style_id for s in style_chain(p.style)]
            heading = next((int(s[-1]) for s in style_ids if re.fullmatch(r"Heading[1-6]", s)), None)
            info = list_info(p)
            if heading:
                attrs.update(kind="heading", heading_level=heading)
            elif info:
                attrs.update(kind="list_item", list_kind=info[0], list_depth=info[1], list_start=info[2])
            elif "DocstreamCode" in style_ids:
                attrs.update(kind="code")
            elif p.style.style_id not in ("Normal", "BodyText"):
                losses.add("PARAGRAPH_STYLE", location(p), "paragraph style maps to supported font properties only: " + p.style.style_id)
            ppr = child.find(qn("w:pPr"))
            if ppr is not None:
                for prop in ppr:
                    if prop.tag.split("}")[-1] not in ("pStyle", "numPr"):
                        losses.add("PARAGRAPH_FORMAT", location(p), "paragraph placement/formatting is unsupported")
            blocks.append(RichBlock(block_id=ident, **attrs))
        elif child.tag == qn("w:tbl"):
            table = Table(child, doc)
            rows = []
            for row in table.rows:
                cells = []
                for cell in row.cells:
                    if cell.tables:
                        losses.add("NESTED_TABLE", "table:" + ident, "nested table content is outside the supported cell paragraphs")
                    cells.append(TableCell(paragraphs=tuple(CellText(runs=paragraph_runs(p,True)) for p in cell.paragraphs) or (CellText(),)))
                trpr = row._tr.find(qn("w:trPr"))
                marker = trpr.find(qn("w:tblHeader")) if trpr is not None else None
                header = marker is not None and marker.get(qn("w:val"), "true") not in ("false", "0", "off")
                rows.append(TableRow(cells=tuple(cells), header=header))
            # Table appearance is deliberately distinct from its rectangular semantic grid.
            if table.style and table.style.style_id not in ("TableNormal", "TableGrid"):
                losses.add("TABLE_STYLE", "table:" + ident, "table appearance is not represented")
            blocks.append(RichBlock(block_id=ident, kind="table", rows=tuple(rows)))
        elif child.tag != qn("w:sectPr"):
            losses.add("BODY_CONTENT", "body:" + ident, "unsupported document body element")
    # Reject impossible/skipped nesting rather than invent parents.
    return Snapshot2(properties=properties, blocks=tuple(blocks)), assets, losses


def preflight_export_text(snapshot):
    """XML 1.0 character repertoire, checked before creating a DOCX document."""
    pending = [(snapshot.model_dump(mode="python"), "snapshot")]
    while pending:
        value, location = pending.pop()
        if isinstance(value, str):
            for offset, char in enumerate(value):
                point = ord(char)
                if not (point in (9, 10, 13) or 0x20 <= point <= 0xD7FF or 0xE000 <= point <= 0xFFFD or 0x10000 <= point <= 0x10FFFF):
                    raise ModelError("UNREPRESENTABLE_DOCX", f"{location}: U+{point:04X} at character {offset} is outside the XML 1.0 repertoire; source text is unchanged")
        elif isinstance(value, dict):
            pending.extend((child, f"{location}.{key}") for key, child in reversed(tuple(value.items())))
        elif isinstance(value, (tuple, list)):
            pending.extend((child, f"{location}[{index}]") for index, child in reversed(tuple(enumerate(value))))


def export_docx(snapshot, get_asset):
    preflight_export_text(snapshot)
    losses = Losses()

    def text_for_docx(text, location):
        if "\r" in text:
            losses.add("DOCX_CARRIAGE_RETURN", location, "each carriage return becomes a line feed on DOCX reimport; existing line feeds remain, including both characters of CRLF")
        return text.replace("\r", "\n")

    doc = Document()
    title = text_for_docx(snapshot.properties.title, "properties.title")
    doc.core_properties.title = title
    doc.core_properties.author = ""
    doc.core_properties.last_modified_by = ""
    doc.core_properties.created = __import__("datetime").datetime(2000,1,1)
    doc.core_properties.modified = __import__("datetime").datetime(2000,1,1)
    section = doc.sections[0]
    section.page_width, section.page_height = Pt(snapshot.properties.page_width_mpt/1000), Pt(snapshot.properties.page_height_mpt/1000)
    section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Pt(72)
    normal = doc.styles["Normal"]
    normal.font.name = snapshot.properties.font_family
    normal.font.size = Pt(snapshot.properties.font_size_mpt/1000)
    normal.font.color.rgb = RGBColor(0,0,0)
    for name in ("Title", *(f"Heading {n}" for n in range(1,7))):
        doc.styles[name].font.color.rgb = RGBColor(0,0,0)
        doc.styles[name].font.name = snapshot.properties.font_family
        rpr=doc.styles[name].element.find(qn("w:rPr"))
        if rpr is not None:
            for prop in list(rpr):
                if prop.tag.split("}")[-1] in ("u","strike","dstrike","highlight","vertAlign","smallCaps","caps","spacing","vanish"):
                    rpr.remove(prop)
    for name, style_type in (("DocstreamCode", 1), ("DocstreamInlineCode", 2)):
        if name not in doc.styles:
            style = doc.styles.add_style(name, style_type)
            style.base_style = normal if style_type==1 else doc.styles["Default Paragraph Font"]
    doc.styles["DocstreamCode"].paragraph_format.space_before = Pt(10)
    doc.styles["DocstreamCode"].paragraph_format.space_after = Pt(10)
    numbering = doc.part.numbering_part.element
    list_stack = []

    def apply_font(run, style):
        if style.font_family is not None:
            run.font.name = style.font_family
        if style.font_size_mpt is not None:
            # Word font size uses half points; report rounding rather than silently lose precision.
            if style.font_size_mpt % 500:
                losses.add("FONT_SIZE_PRECISION", "export", "Word font sizes have half-point precision")
            run.font.size = Pt(style.font_size_mpt/1000)
        run.bold, run.italic = style.bold, style.italic

    def add_runs(paragraph, runs, block_style=Style(), location="export", plain=False):
        for index, span in enumerate(runs):
            path = f"{location}.text" if plain else f"{location}.runs[{index}].text"
            run = paragraph.add_run(text_for_docx(span.text, path))
            if span.code:
                run.style = "DocstreamInlineCode"
            values = {k: v if v is not None else getattr(block_style,k) for k,v in span.style.model_dump().items()}
            apply_font(run, Style(**values))
            if span.href:
                relation = paragraph.part.relate_to(span.href, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
                link = el("w:hyperlink", **{"r:id":relation})
                paragraph._p.remove(run._r)
                link.append(run._r)
                paragraph._p.append(link)

    def num_id(block):
        depth = getattr(block,"list_depth",0)
        key = (block.list_kind, getattr(block,"list_start",1))
        del list_stack[depth+1:]
        if len(list_stack) > depth and list_stack[depth][0] == key:
            return list_stack[depth][1]
        del list_stack[depth:]
        abstract_id = max([int(n.get(qn("w:abstractNumId"))) for n in numbering.findall(qn("w:abstractNum"))] or [-1])+1
        abstract = el("w:abstractNum", **{"w:abstractNumId":abstract_id})
        abstract.append(el("w:multiLevelType", **{"w:val":"multilevel"}))
        for level in range(9):
            lvl = el("w:lvl", **{"w:ilvl":level})
            for tag, value in (("start",key[1]), ("numFmt","decimal" if key[0]=="ordered" else "bullet"), ("lvlText",f"%{level+1}." if key[0]=="ordered" else "•"), ("lvlJc","left")):
                lvl.append(el("w:"+tag, **{"w:val":value}))
            ppr = el("w:pPr")
            ppr.append(el("w:ind", **{"w:left":360*(level+1), "w:hanging":180}))
            lvl.append(ppr)
            abstract.append(lvl)
        numbering.append(abstract)
        number = numbering.add_num(abstract_id).numId
        list_stack.append((key, number))
        return number

    if snapshot.properties.title:
        doc.add_paragraph(title, "Title")
    for block_index, b in enumerate(snapshot.blocks):
        location = f"blocks[{block_index}]"
        if b.kind != "list_item":
            list_stack.clear()
        if b.kind == "table":
            table = doc.add_table(rows=len(b.rows), cols=len(b.rows[0].cells))
            table.style = "Table Grid"
            borders = el("w:tblBorders")
            for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
                borders.append(el("w:"+side, **{"w:val":"single", "w:sz":"4", "w:color":"D9D9D9"}))
            table._tbl.tblPr.append(borders)
            for row_index, row in enumerate(b.rows):
                if row.header:
                    table.rows[row_index]._tr.get_or_add_trPr().append(el("w:tblHeader", **{"w:val":"true"}))
                for col, cell in enumerate(row.cells):
                    target = table.cell(row_index,col)
                    target.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    for index, paragraph in enumerate(cell.paragraphs):
                        p = target.paragraphs[0] if index == 0 else target.add_paragraph()
                        add_runs(p, paragraph.runs, b.style, f"{location}.rows[{row_index}].cells[{col}].paragraphs[{index}]")
                    tcpr = target._tc.get_or_add_tcPr()
                    if row.header:
                        tcpr.append(el("w:shd", **{"w:val":"clear", "w:fill":"EDF1F5"}))
                    margins = el("w:tcMar")
                    for side in ("top","bottom","left","right"):
                        margins.append(el("w:"+side, **{"w:w":"100", "w:type":"dxa"}))
                    tcpr.append(margins)
            continue
        if b.kind == "image":
            raw = get_asset(b.image.sha256)
            p = doc.add_paragraph()
            picture = p.add_run().add_picture(BytesIO(raw), width=Pt(b.image.width_mpt/1000), height=Pt(b.image.height_mpt/1000))
            picture._inline.docPr.set("descr", b.image.alt)
            continue
        p = doc.add_paragraph(style=(f"Heading {b.heading_level}" if b.kind == "heading" else "DocstreamCode" if b.kind == "code" else "Normal"))
        if b.kind == "list_item":
            numpr = p._p.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = getattr(b,"list_depth",0)
            numpr.get_or_add_numId().val = num_id(b)
        runs = getattr(b,"runs",()) or (Span(text=b.text),)
        add_runs(p, runs, b.style, location, plain=not getattr(b, "runs", ()))
    if snapshot.properties.font_size_mpt % 500:
        losses.add("FONT_SIZE_PRECISION", "document", "Word default font size has half-point precision")
    output = BytesIO()
    doc.save(output)
    # Stabilize container metadata; this is semantic export, not original ZIP reproduction.
    with __import__("zipfile").ZipFile(BytesIO(output.getvalue())) as archive:
        entries = {name:archive.read(name) for name in archive.namelist()}
    return deterministic_zip(entries), losses
