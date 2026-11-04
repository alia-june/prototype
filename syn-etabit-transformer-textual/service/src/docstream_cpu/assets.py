"""Managed image bytes reuse the transactional, hash-checked source store."""
from hashlib import sha256
from io import BytesIO
import warnings

from PIL import Image

from .catalog import Source
from .errors import ModelError

MAX_ASSET = 1_048_576


def validate_image(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_ASSET:
        raise ModelError("ASSET_LIMIT", "image must be nonempty and at most 1 MiB")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as image:
                if image.format not in ("PNG", "JPEG") or image.width * image.height > 16_000_000:
                    raise ValueError("unsupported image format or dimensions")
                if getattr(image, "n_frames", 1) != 1:
                    raise ValueError("animated images are unsupported")
                result = ("image/png" if image.format == "PNG" else "image/jpeg", image.width, image.height)
                image.verify()
        return result
    except Exception as exc:
        raise ModelError("INVALID_IMAGE", "image must be a valid static PNG/JPEG within the pixel limit") from exc


class AssetStore:
    def __init__(self, store):
        self.store = store

    def put(self, raw):
        media, _, _ = validate_image(raw)
        key = "asset:" + sha256(raw).hexdigest()
        self.store.model._sources.setdefault(key, Source(key, raw, media))
        return key[6:]

    def get(self, content_hash):
        key = "asset:" + content_hash
        source = self.store.model._sources.get(key)
        if source is None or source.original_sha256 != content_hash:
            raise ModelError("ASSET_UNAVAILABLE", "image bytes are absent or damaged")
        return source.original_bytes


def validate_references(snapshot, getter):
    for block in snapshot.blocks:
        image = getattr(block, "image", None)
        if image:
            raw = getter(image.sha256)
            media, _, _ = validate_image(raw)
            if sha256(raw).hexdigest() != image.sha256 or media != image.media_type:
                raise ModelError("ASSET_INTEGRITY", "image does not match its semantic reference")
