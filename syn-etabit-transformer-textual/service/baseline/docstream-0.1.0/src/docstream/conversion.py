from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

from .core import (
    DocumentError,
    append_audit,
    atomic_write_text,
    default_audit_path,
    file_sha256,
)


@dataclass(frozen=True)
class ConversionResult:
    source: str
    output: str
    backend: str
    source_sha256: str
    output_sha256: str
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _pandoc_path(explicit: str | None = None) -> str | None:
    if explicit:
        candidate = Path(explicit)
        if candidate.is_file():
            return str(candidate.resolve())
        found = shutil.which(explicit)
        if found:
            return found
        raise DocumentError(f"Pandoc executable not found: {explicit}")
    return shutil.which("pandoc")


def choose_backend(requested: str, pandoc: str | None = None) -> tuple[str, str | None]:
    resolved = _pandoc_path(pandoc)
    if requested == "pandoc":
        if not resolved:
            raise DocumentError(
                "Pandoc is not available. Install it or use --backend native for standard documents."
            )
        return "pandoc", resolved
    if requested == "native":
        return "native", None
    if requested != "auto":
        raise DocumentError(f"unknown conversion backend: {requested}")
    return ("pandoc", resolved) if resolved else ("native", None)


def import_docx(
    source: Path,
    output: Path,
    *,
    backend: str = "auto",
    pandoc: str | None = None,
    force: bool = False,
    audit_path: Path | None = None,
) -> ConversionResult:
    if not source.is_file():
        raise DocumentError(f"DOCX source does not exist: {source}")
    if output.exists() and not force:
        raise DocumentError(f"refusing to overwrite existing file: {output}")
    selected, executable = choose_backend(backend, pandoc)
    warnings: list[str] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    if selected == "pandoc":
        command = [executable or "pandoc", str(source), "-t", "gfm", "--wrap=none", "-o", str(output)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        if completed.returncode:
            raise DocumentError(f"Pandoc import failed: {completed.stderr.strip()}")
    else:
        content, warnings = _native_docx_to_markdown(source)
        atomic_write_text(output, content)
    result = ConversionResult(
        source=str(source.resolve()),
        output=str(output.resolve()),
        backend=selected,
        source_sha256=file_sha256(source),
        output_sha256=file_sha256(output),
        warnings=warnings,
    )
    append_audit(
        audit_path or default_audit_path(output),
        {"operation": "import", "result": result.to_dict()},
    )
    return result


def publish_docx(
    source: Path,
    output: Path,
    *,
    backend: str = "auto",
    pandoc: str | None = None,
    reference_doc: Path | None = None,
    force: bool = False,
    audit_path: Path | None = None,
) -> ConversionResult:
    if not source.is_file():
        raise DocumentError(f"Markdown source does not exist: {source}")
    if output.exists() and not force:
        raise DocumentError(f"refusing to overwrite existing file: {output}")
    if reference_doc and not reference_doc.is_file():
        raise DocumentError(f"reference DOCX does not exist: {reference_doc}")
    selected, executable = choose_backend(backend, pandoc)
    warnings: list[str] = []
    output.parent.mkdir(parents=True, exist_ok=True)
    if selected == "pandoc":
        command = [executable or "pandoc", str(source), "-f", "gfm", "-o", str(output)]
        if reference_doc:
            command.extend(["--reference-doc", str(reference_doc)])
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        if completed.returncode:
            raise DocumentError(f"Pandoc publish failed: {completed.stderr.strip()}")
    else:
        if reference_doc:
            warnings.append("native backend does not apply reference DOCX styling; use Pandoc for templates")
        warnings.extend(_native_markdown_to_docx(source, output))
    result = ConversionResult(
        source=str(source.resolve()),
        output=str(output.resolve()),
        backend=selected,
        source_sha256=file_sha256(source),
        output_sha256=file_sha256(output),
        warnings=warnings,
    )
    append_audit(
        audit_path or default_audit_path(source),
        {"operation": "publish", "result": result.to_dict()},
    )
    return result


def _load_docx() -> tuple[Any, Any, Any, Any]:
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.enum.text import WD_BREAK
        from docx.shared import Inches, Pt
    except ImportError as exc:
        raise DocumentError(
            "native conversion requires python-docx; install the package or use Pandoc"
        ) from exc
    return Document, WD_STYLE_TYPE, (WD_BREAK, Inches), Pt


def _escape_markdown(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").strip()


def _native_docx_to_markdown(source: Path) -> tuple[str, list[str]]:
    Document, _, _, _ = _load_docx()
    from docx.table import Table

    document = Document(str(source))
    chunks: list[str] = []
    warnings = [
        "native import preserves standard paragraphs, headings, lists, and tables; complex Word fields, text boxes, comments, revisions, and floating media may be omitted"
    ]
    title_seen = False
    for block in document.iter_inner_content():
        if isinstance(block, Table):
            rows = [[_escape_markdown(cell.text) for cell in row.cells] for row in block.rows]
            if not rows:
                continue
            width = max(len(row) for row in rows)
            rows = [row + [""] * (width - len(row)) for row in rows]
            table_lines = ["| " + " | ".join(rows[0]) + " |"]
            table_lines.append("| " + " | ".join(["---"] * width) + " |")
            table_lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
            chunks.append("\n".join(table_lines))
            continue
        text = block.text.strip()
        if not text:
            continue
        style = (block.style.name if block.style else "").lower()
        if style == "title" and not title_seen:
            chunks.append(f"# {text}")
            title_seen = True
        elif style.startswith("heading"):
            match = re.search(r"(\d+)", style)
            level = min(6, int(match.group(1)) + 1) if match else 2
            chunks.append(f"{'#' * level} {text}")
        elif "list bullet" in style:
            chunks.append(f"- {text}")
        elif "list number" in style:
            chunks.append(f"1. {text}")
        else:
            chunks.append(text)
    content = "\n\n".join(chunks).rstrip() + "\n"
    return content, warnings


INLINE = re.compile(r"(\*\*.+?\*\*|(?<!\*)\*[^*]+?\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def _add_inline(paragraph: Any, text: str) -> None:
    cursor = 0
    for match in INLINE.finditer(text):
        if match.start() > cursor:
            paragraph.add_run(text[cursor : match.start()])
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
        elif token.startswith("["):
            label, target = re.match(r"\[([^\]]+)\]\(([^)]+)\)", token).groups()
            paragraph.add_run(f"{label} ({target})")
        cursor = match.end()
    if cursor < len(text):
        paragraph.add_run(text[cursor:])


def _table_row(line: str) -> list[str]:
    return [
        cell.strip().replace("\\|", "|")
        for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))
    ]


def _is_table_separator(line: str) -> bool:
    cells = _table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _native_markdown_to_docx(source: Path, output: Path) -> list[str]:
    Document, WD_STYLE_TYPE, _, Pt = _load_docx()
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, RGBColor

    document = Document()
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)
    styles = document.styles
    for name, size, bold in [("Normal", 11, False), ("Title", 22, True), ("Heading 1", 16, True), ("Heading 2", 13, True)]:
        style = styles[name]
        style.font.name = "Aptos"
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.color.rgb = RGBColor(0, 0, 0)
    styles["Normal"].paragraph_format.space_after = Pt(7)
    styles["Normal"].paragraph_format.line_spacing = 1.08

    lines = source.read_text(encoding="utf-8").splitlines()
    index = 0
    first_heading = True
    in_code = False
    code_lines: list[str] = []
    warnings = [
        "native publish supports ATX headings, paragraphs, lists, blockquotes, fenced code, pipe tables, bold, italic, inline code, and visible link targets"
    ]

    def shade(cell: Any, fill: str) -> None:
        properties = cell._tc.get_or_add_tcPr()
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), fill)
        properties.append(shading)

    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            if in_code:
                paragraph = document.add_paragraph()
                paragraph.style = styles["Normal"]
                run = paragraph.add_run("\n".join(code_lines))
                run.font.name = "Consolas"
                run.font.size = Pt(9.5)
                code_lines = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not line.strip():
            index += 1
            continue
        if index + 1 < len(lines) and "|" in line and _is_table_separator(lines[index + 1]):
            rows = [_table_row(line)]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(_table_row(lines[index]))
                index += 1
            width = max(len(row) for row in rows)
            table = document.add_table(rows=len(rows), cols=width)
            table.style = "Table Grid"
            for row_number, row in enumerate(rows):
                for column, value in enumerate(row):
                    cell = table.cell(row_number, column)
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    _add_inline(cell.paragraphs[0], value)
                    if row_number == 0:
                        shade(cell, "D9EAF7")
                        for run in cell.paragraphs[0].runs:
                            run.bold = True
            document.add_paragraph()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2)
            if level == 1 and first_heading:
                paragraph = document.add_paragraph(style="Title")
                first_heading = False
            else:
                paragraph = document.add_paragraph(style=f"Heading {min(level, 9)}")
            _add_inline(paragraph, text)
            index += 1
            continue
        bullet = re.match(r"^\s*[-*+]\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if bullet or numbered:
            paragraph = document.add_paragraph(
                style="List Bullet" if bullet else "List Number"
            )
            _add_inline(paragraph, (bullet or numbered).group(1))
            index += 1
            continue
        if line.startswith("> "):
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Inches(0.3)
            run = paragraph.add_run(line[2:])
            run.italic = True
            index += 1
            continue
        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines) and lines[index].strip():
            candidate = lines[index]
            if candidate.startswith(("#", "```", "> ")) or re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", candidate):
                break
            if index + 1 < len(lines) and "|" in candidate and _is_table_separator(lines[index + 1]):
                break
            paragraph_lines.append(candidate.strip())
            index += 1
        paragraph = document.add_paragraph()
        _add_inline(paragraph, " ".join(paragraph_lines))
    if in_code:
        warnings.append("unclosed fenced code block was published as code through end of file")
        paragraph = document.add_paragraph()
        run = paragraph.add_run("\n".join(code_lines))
        run.font.name = "Consolas"
    document.save(str(output))
    return warnings

