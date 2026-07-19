"""Deterministic CSS/HTML style extraction for the website path.

Pulls raw color and dimension values out of stylesheet/inline text with regex,
counting occurrences. Clustering + semantic naming happens downstream.
"""
import re
from collections import Counter

_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
_RGB = re.compile(r"rgba?\([^)]*\)")
_FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9.]+(?:px|rem|em|pt))", re.I)
_FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;{}]+)", re.I)
_RADIUS = re.compile(r"border-radius\s*:\s*([0-9.]+(?:px|rem|em|%))", re.I)


def _norm_hex(h):
    h = h.lower()
    if len(h) == 4:  # #abc -> #aabbcc
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def extract(css_text):
    """Return {category: Counter(value -> occurrence_count)}."""
    colors = Counter(_norm_hex(m) for m in _HEX.findall(css_text))
    colors.update(m.lower().replace(" ", "") for m in _RGB.findall(css_text))
    return {
        "color": colors,
        "fontSize": Counter(m.lower() for m in _FONT_SIZE.findall(css_text)),
        "fontFamily": Counter(m.strip().strip("'\"").split(",")[0].strip()
                              for m in _FONT_FAMILY.findall(css_text)),
        "radius": Counter(m.lower() for m in _RADIUS.findall(css_text)),
    }
