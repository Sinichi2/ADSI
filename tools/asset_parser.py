"""Favicon/logo sniffing for the website path. Same regex-over-raw-HTML style as style_parser."""
import re
from urllib.parse import urljoin

_ICON_LINK = re.compile(
    r'<link[^>]+rel=["\'](?:shortcut icon|icon|apple-touch-icon)["\'][^>]+href=["\']([^"\']+)["\']', re.I)
_LOGO_IMG = re.compile(r'<img[^>]+(?:src|alt)=["\']([^"\']*logo[^"\']*)["\']', re.I)
_SRC = re.compile(r'src=["\']([^"\']+)["\']', re.I)


def extract(html_text, base_url):
    """Return {"logo": [...abs urls], "icon": [...abs urls]}, most-likely match first."""
    icons = [urljoin(base_url, m) for m in _ICON_LINK.findall(html_text or "")]
    logos = []
    for tag_start in (m.start() for m in re.finditer(r"<img\b", html_text or "", re.I)):
        tag = html_text[tag_start: html_text.index(">", tag_start) + 1]
        if _LOGO_IMG.search(tag):
            src = _SRC.search(tag)
            if src:
                logos.append(urljoin(base_url, src.group(1)))
    return {"logo": logos, "icon": icons}


def demo():
    html = (
        '<link rel="icon" href="/favicon.ico">'
        '<img src="/img/company-logo.png" alt="Acme logo">'
        '<img src="/img/hero.jpg" alt="hero shot">'
    )
    out = extract(html, "https://example.com/about")
    assert out["icon"] == ["https://example.com/favicon.ico"], out
    assert out["logo"] == ["https://example.com/img/company-logo.png"], out
    print("asset_parser: OK")


if __name__ == "__main__":
    demo()
