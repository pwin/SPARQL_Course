# -*- coding: utf-8 -*-
"""The Semantechs mark, as a data URI.

Published pages carry their images with them: the artifact CSP admits scripts
from a short list of CDNs and nothing else, so an <img src> pointing anywhere
would simply fail to load. The mark is therefore resized once and inlined.

The repository copy in assets/ is the one GitHub renders in the README.
"""
from __future__ import annotations

import base64
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "semantechs-logo.png"

# Big enough to look right at 40px on a high-density display, small enough
# that the base64 does not dominate the page.
EMBED_PX = 96


def data_uri(px: int = EMBED_PX) -> str:
    """The mark as a base64 PNG data URI, or an empty string if it is absent."""
    if not SOURCE.exists():
        return ""
    try:
        from PIL import Image
    except ImportError:
        return "data:image/png;base64," + base64.b64encode(
            SOURCE.read_bytes()).decode("ascii")
    img = Image.open(SOURCE).convert("RGBA").resize((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def favicon_link(px: int = 32) -> str:
    """A <link rel="icon"> carrying the mark inline.

    Published artifacts take their tab icon from the platform, which accepts
    an emoji rather than an image, so this applies to the files themselves --
    opened locally, or served from GitHub Pages.
    """
    uri = data_uri(px)
    if not uri:
        return ""
    return f'<link rel="icon" type="image/png" href="{uri}">'


def write_favicon(path: Path, px: int = 32) -> None:
    """Also drop a real favicon.png next to the page, for hosts that want one."""
    if not SOURCE.exists():
        return
    try:
        from PIL import Image
    except ImportError:
        return
    img = Image.open(SOURCE).convert("RGBA").resize((px, px), Image.LANCZOS)
    img.save(path, format="PNG", optimize=True)


def img_tag(css_class: str = "logo", alt: str = "Semantechs", px: int = EMBED_PX) -> str:
    uri = data_uri(px)
    if not uri:
        return ""
    return f'<img class="{css_class}" src="{uri}" alt="{alt}" width="{px}" height="{px}">'
