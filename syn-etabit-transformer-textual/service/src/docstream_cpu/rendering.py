"""Versioned HTML construction and a warm, bounded Chromium worker process."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from hashlib import sha256
from html import escape
import importlib.metadata
import json
import math
import multiprocessing
import os
from pathlib import Path
import threading
from uuid import uuid4
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from .errors import ModelError
from .models import Snapshot, Value, digest

RENDERER_VERSION = "docstream.html/2"
SERVICE_ROOT = Path(__file__).resolve().parents[2]


class RenderProfile(Value):
    schema_version: Literal["docstream.render/1"] = "docstream.render/1"
    formats: tuple[Literal["png", "pdf"], ...] = ("png", "pdf")
    margin_mpt: Annotated[int, Field(ge=0, le=144000)] = 36000
    show_title: bool = True
    code_font_family: str = "Consolas"
    locale: Literal["en-US", "en-GB"] = "en-US"
    max_height_px: Annotated[int, Field(ge=500, le=16000)] = 12000

    @field_validator("formats", mode="before")
    @classmethod
    def array(cls, value):
        return tuple(value) if type(value) is list else value

    @model_validator(mode="after")
    def formats_unique(self):
        if not self.formats or len(self.formats) != len(set(self.formats)):
            raise ValueError("formats must be nonempty and unique")
        return self


def file_digest(path: Path):
    value = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


class FontRegistry:
    """Explicit local font files; no caller paths and no silent family aliases."""
    def __init__(self):
        root = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        self.fonts = {}
        for family, names in {
            "Arial": ("arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
            "Times New Roman": ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"),
            "Consolas": ("consola.ttf", "consolab.ttf", "consolai.ttf", "consolaz.ttf"),
        }.items():
            paths = tuple(root / name for name in names)
            if all(path.is_file() for path in paths):
                self.fonts[family] = tuple((path, file_digest(path)) for path in paths)

    def resolve(self, family: str):
        if family not in self.fonts:
            raise ModelError("FONT_UNAVAILABLE", f"font is not registered: {family}")
        return self.fonts[family]


@dataclass(frozen=True)
class RenderSpec:
    cache_key: str
    html: str
    profile: RenderProfile
    width: int
    height: int
    metadata: dict


def _worker(connection, executable: str):
    """Spawn target: all Playwright objects remain on this process's main thread."""
    playwright = browser = None
    try:
        while True:
            command = connection.recv()
            if command["op"] == "stop":
                break
            try:
                if browser is None or not browser.is_connected():
                    if playwright is None:
                        from playwright.sync_api import sync_playwright
                        playwright = sync_playwright().start()
                    browser = playwright.chromium.launch(executable_path=executable, headless=True,
                        args=["--disable-gpu", "--disable-background-networking", "--disable-component-update", "--no-first-run"])
                context = browser.new_context(viewport={"width": command["width"], "height": command["height"]},
                    device_scale_factor=1, locale=command["profile"]["locale"], timezone_id="UTC",
                    java_script_enabled=False, service_workers="block")
                try:
                    context.route("**/*", lambda route: route.abort())
                    page = context.new_page()
                    page.set_default_timeout(15000)
                    page.set_content(command["html"], wait_until="load", timeout=15000)
                    page.evaluate("document.fonts.ready")
                    metrics = page.evaluate("({height:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight),width:document.documentElement.scrollWidth})")
                    if metrics["height"] > command["profile"]["max_height_px"] or metrics["width"] > command["width"] + 1:
                        raise ModelError("RENDER_LIMIT", "document exceeds preview dimensions")
                    session = context.new_cdp_session(page)
                    session.send("DOM.enable")
                    session.send("CSS.enable")
                    document = session.send("DOM.getDocument")
                    ids = session.send("DOM.querySelectorAll", {"nodeId": document["root"]["nodeId"], "selector": "[data-ds-text]"})["nodeIds"]
                    font_usage = {}
                    for node in ids:
                        used = session.send("CSS.getPlatformFontsForNode", {"nodeId": node})["fonts"]
                        if any(font["glyphCount"] > 0 and not font["isCustomFont"] for font in used):
                            raise ModelError("FONT_GLYPH_UNAVAILABLE", "a glyph requires an unregistered fallback font")
                        for font in used:
                            key = (font["familyName"], font["postScriptName"], font["isCustomFont"])
                            if key not in font_usage:
                                font_usage[key] = {**font, "glyphCount": 0}
                            font_usage[key]["glyphCount"] += font["glyphCount"]
                    files = {}
                    if "png" in command["profile"]["formats"]:
                        files["png"] = page.screenshot(full_page=True, animations="disabled", timeout=30000)
                    if "pdf" in command["profile"]["formats"]:
                        files["pdf"] = page.pdf(prefer_css_page_size=True, print_background=True)
                    response = {"ok": True, "files": files, "metadata": {"browser_version": browser.version,
                        "font_usage": list(font_usage.values()), "width_px": command["width"], "height_px": metrics["height"]}}
                finally:
                    context.close()
                connection.send(response)
            except Exception as exc:
                connection.send({"ok": False, "code": getattr(exc, "code", "RENDER_FAILED"),
                                 "message": str(exc)[:500] if isinstance(exc, ModelError) else "browser rendering failed"})
    except (EOFError, BrokenPipeError):
        pass
    finally:
        if browser is not None:
            browser.close()
        if playwright is not None:
            playwright.stop()
        connection.close()


class Renderer:
    def __init__(self, browser_root: Path | None = None):
        self.fonts = FontRegistry()
        self.browser_root = browser_root or SERVICE_ROOT / ".browsers"
        self._identity = None
        self._lock = threading.RLock()
        self.process = self.connection = self.job = None
        self.starts = self.render_count = 0

    def identity(self):
        if self._identity is None:
            import playwright
            package = Path(playwright.__file__).parent
            entries = json.loads((package / "driver" / "package" / "browsers.json").read_text())["browsers"]
            entry = next(item for item in entries if item["name"] == "chromium")
            executable = self.browser_root / ("chromium-" + entry["revision"]) / "chrome-win64" / "chrome.exe"
            library = executable.parent / "chrome.dll"
            if not executable.is_file() or not library.is_file():
                raise ModelError("RENDER_UNAVAILABLE", "project-local Chromium is not installed")
            self.executable = executable
            self._identity = {"renderer": RENDERER_VERSION, "playwright": importlib.metadata.version("playwright"),
                              "browser_revision": entry["revision"], "browser_version": entry["browserVersion"],
                              "executable_sha256": file_digest(executable), "engine_sha256": file_digest(library)}
        return self._identity

    def prepare(self, snapshot: Snapshot, profile: RenderProfile, get_asset=None) -> RenderSpec:
        identity = self.identity()
        width_pt = snapshot.properties.page_width_mpt / 1000
        height_pt = snapshot.properties.page_height_mpt / 1000
        margin = profile.margin_mpt / 1000
        if not (144 <= width_pt <= 1440 and 144 <= height_pt <= 2000) or margin * 2 >= min(width_pt, height_pt):
            raise ModelError("RENDER_LIMIT", "page dimensions or margins are outside the rendering profile")
        families = {snapshot.properties.font_family}
        families.update(block.style.font_family for block in snapshot.blocks if block.style.font_family)
        from .rich import Snapshot2, style_nodes
        if isinstance(snapshot, Snapshot2):
            families.update(style.font_family for b in snapshot.blocks for style in style_nodes(b).values() if style.font_family)
        if not isinstance(snapshot, Snapshot2) and any(block.kind == "code" and not block.style.font_family for block in snapshot.blocks):
            families.add(profile.code_font_family)
        faces, aliases, font_identity = [], {}, {}
        for number, family in enumerate(sorted(families)):
            files = self.fonts.resolve(family)
            aliases[family] = f"DSFont{number}"
            font_identity[family] = [hash_value for _, hash_value in files]
            for index, (path, expected) in enumerate(files):
                raw = path.read_bytes()
                if sha256(raw).hexdigest() != expected:
                    raise ModelError("FONT_CHANGED", "registered font file changed; restart renderer")
                encoded = base64.b64encode(raw).decode()
                weight = "bold" if index in (1, 3) else "normal"
                style = "italic" if index in (2, 3) else "normal"
                faces.append(f"@font-face{{font-family:{aliases[family]};src:url(data:font/ttf;base64,{encoded});font-weight:{weight};font-style:{style}}}")
        default_alias = aliases[snapshot.properties.font_family]
        css = f"""@page{{size:{width_pt}pt {height_pt}pt;margin:{margin}pt}}
*{{box-sizing:border-box;font-synthesis:none}}html{{background:#fff}}body{{margin:0;width:{width_pt}pt;padding:{margin}pt;color:#17212b;background:#fff;font-family:{default_alias};font-size:{snapshot.properties.font_size_mpt/1000}pt;line-height:1.5}}
h1,h2,h3,h4,h5,h6{{line-height:1.2;margin:18pt 0 8pt;break-after:avoid}}.doc-title{{font-size:24pt;color:#173b5e;margin:0 0 22pt}}
p{{margin:0 0 10pt}}pre{{background:#f2f5f8;padding:10pt;border-left:3pt solid #577f9f;white-space:pre-wrap}}[data-ds-text]{{white-space:pre-wrap;overflow-wrap:anywhere}}ul,ol{{margin:6pt 0 12pt;padding-left:22pt}}li{{margin-bottom:4pt}}
@media print{{body{{width:auto;padding:0}}}}"""
        parts = []
        if profile.show_title and snapshot.properties.title:
            parts.append(f'<h1 class="doc-title" data-ds-text>{escape(snapshot.properties.title)}</h1>')
        list_tag = None
        legacy_blocks = snapshot.blocks
        if isinstance(snapshot, Snapshot2):
            from .rich_rendering import CSS, build
            css += CSS
            parts.append(build(snapshot, profile, aliases, get_asset))
            legacy_blocks = ()
        for index, block in enumerate(legacy_blocks):
            desired = ("ol" if block.list_kind == "ordered" else "ul") if block.kind == "list_item" else None
            if desired != list_tag:
                if list_tag:
                    parts.append(f"</{list_tag}>")
                if desired:
                    parts.append(f"<{desired}>")
                list_tag = desired
            family = block.style.font_family or (profile.code_font_family if block.kind == "code" else snapshot.properties.font_family)
            size = block.style.font_size_mpt
            styles = [f"font-family:{aliases[family]}"]
            if size is not None:
                styles.append(f"font-size:{size/1000}pt")
            if block.style.bold is not None:
                styles.append("font-weight:" + ("bold" if block.style.bold else "normal"))
            if block.style.italic is not None:
                styles.append("font-style:" + ("italic" if block.style.italic else "normal"))
            tag = "h" + str(block.heading_level) if block.kind == "heading" else "pre" if block.kind == "code" else "li" if block.kind == "list_item" else "p"
            parts.append(f'<{tag} id="ds-{index}" data-ds-text style="{";".join(styles)}">{escape(block.text)}</{tag}>')
        if list_tag:
            parts.append(f"</{list_tag}>")
        html = '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; font-src data:; img-src data:; script-src \'none\'"><style>' + "".join(faces) + css + "</style></head><body>" + "".join(parts) + "</body></html>"
        metadata = {**identity, "semantic_sha256": snapshot.digest, "fonts": font_identity,
                    "profile": profile.model_dump(mode="json"), "html_sha256": sha256(html.encode()).hexdigest()}
        return RenderSpec(digest(metadata), html, profile, math.ceil(width_pt * 96 / 72), math.ceil(height_pt * 96 / 72), metadata)

    def _start(self):
        context = multiprocessing.get_context("spawn")
        parent, child = context.Pipe()
        self.process = context.Process(target=_worker, args=(child, str(self.executable)), daemon=True)
        self.process.start()
        child.close()
        self.connection = parent
        if os.name == "nt":
            import win32api, win32con, win32job
            try:
                self.job = win32job.CreateJobObject(None, "Docstream-" + uuid4().hex)
                info = win32job.QueryInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation)
                info["BasicLimitInformation"]["LimitFlags"] = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                win32job.SetInformationJobObject(self.job, win32job.JobObjectExtendedLimitInformation, info)
                process_handle = win32api.OpenProcess(win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE, False, self.process.pid)
                try:
                    win32job.AssignProcessToJobObject(self.job, process_handle)
                finally:
                    process_handle.Close()
            except Exception as exc:
                self.close()
                raise ModelError("RENDER_UNAVAILABLE", "could not establish renderer process ownership") from exc
        self.starts += 1

    def render(self, spec: RenderSpec):
        with self._lock:
            if self.process is None or not self.process.is_alive():
                self.close()
                self._start()
            self.connection.send({"op": "render", "html": spec.html, "width": spec.width, "height": spec.height,
                                  "profile": spec.profile.model_dump(mode="json")})
            if not self.connection.poll(60):
                self.close()
                raise ModelError("RENDER_TIMEOUT", "renderer exceeded its 60-second budget")
            try:
                result = self.connection.recv()
            except (EOFError, OSError) as exc:
                self.close()
                raise ModelError("RENDER_FAILED", "renderer process exited") from exc
            if not result["ok"]:
                raise ModelError(result["code"], result["message"])
            if result["metadata"]["browser_version"] != spec.metadata["browser_version"]:
                raise ModelError("RENDER_IDENTITY", "actual Chromium differs from the cache profile")
            self.render_count += 1
            return result

    def close(self):
        with self._lock:
            if self.process is not None:
                if self.process.is_alive() and self.connection is not None:
                    try:
                        self.connection.send({"op": "stop"})
                    except (BrokenPipeError, OSError):
                        pass
                    self.process.join(3)
                if self.job is not None:
                    self.job.Close()
                    self.job = None
                if self.process.is_alive():
                    self.process.terminate()
                self.process.join(5)
                if self.process.is_alive():
                    raise ModelError("RENDER_SHUTDOWN", "renderer worker did not stop")
                self.process.close()
                self.process = None
            if self.connection is not None:
                self.connection.close()
                self.connection = None
