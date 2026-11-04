"""Conversion reports and bounded ZIP/XML ingestion shared by adapters."""
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import PurePosixPath
import zipfile

from lxml import etree

from .errors import ModelError

MAX_SOURCE = 1_048_576
MAX_EXPANDED = 16 * 1_048_576
MAX_ENTRIES = 256


class ConversionError(ModelError):
    def __init__(self, diagnostics):
        super().__init__("CONVERSION_LOSS", "conversion would lose unsupported features; inspect diagnostics and choose loss_policy=allow only when intended")
        self.diagnostics = diagnostics


@dataclass
class Losses:
    items: list = field(default_factory=list)

    def add(self, code, location, detail):
        item = {"code": code[:128], "location": location[:256], "detail": detail[:500]}
        if item not in self.items:
            self.items.append(item)
        if len(self.items) > 100:
            raise ModelError("DIAGNOSTIC_LIMIT", "more than 100 conversion losses; narrow the source")

    def check(self, policy):
        if self.items and policy == "reject":
            raise ConversionError(self.items)


def safe_asset_name(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and not any(p in (".", "..") for p in name.split("/")) and "\\" not in name and ":" not in name and "\x00" not in name


def read_package(raw):
    if not 0 < len(raw) <= MAX_SOURCE:
        raise ModelError("SOURCE_LIMIT", "source package must be nonempty and at most 1 MiB")
    try:
        with zipfile.ZipFile(BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ENTRIES or sum(e.file_size for e in entries) > MAX_EXPANDED:
                raise ModelError("PACKAGE_LIMIT", "package exceeds entry or expanded-byte limit")
            result, names = {}, set()
            for entry in entries:
                name = entry.filename
                if entry.orig_filename != name:
                    raise ModelError("INVALID_PACKAGE", "package entry was normalized by the ZIP reader")
                if not safe_asset_name(name.rstrip("/")) or name.casefold().rstrip("/") in names or entry.flag_bits & 1 or entry.external_attr >> 16 & 0o170000 == 0o120000:
                    raise ModelError("INVALID_PACKAGE", "unsafe, duplicate, encrypted or linked package entry")
                names.add(name.casefold().rstrip("/"))
                if entry.is_dir():
                    continue
                if entry.file_size > MAX_EXPANDED or (entry.file_size > 1_048_576 and entry.file_size > max(1, entry.compress_size) * 200):
                    raise ModelError("PACKAGE_LIMIT", "package entry exceeds expansion limit")
                result[name] = archive.read(entry)
            return result
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise ModelError("INVALID_PACKAGE", "invalid ZIP package") from exc


def xml(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ModelError("INVALID_XML", "document type and entity declarations are unsupported")
    try:
        tree = etree.fromstring(raw, etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False))
        if tree.getroottree().docinfo.doctype:
            raise ModelError("INVALID_XML", "document type declarations are unsupported")
        return tree
    except etree.XMLSyntaxError as exc:
        raise ModelError("INVALID_XML", "invalid XML") from exc


def deterministic_zip(entries):
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, raw)
    return output.getvalue()
