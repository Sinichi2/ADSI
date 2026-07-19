"""Firecrawl crawl/render wrapper for the website path. Lazy — only import when used."""
import os


def scrape(url, api_key=None):
    """Return concatenated HTML+CSS text for a URL. Raises if firecrawl unavailable."""
    key = api_key or os.getenv("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY not set.")
    try:
        from firecrawl import FirecrawlApp
    except ImportError as e:
        raise RuntimeError("pip install firecrawl-py") from e
    app = FirecrawlApp(api_key=key)
    res = app.scrape_url(url, params={"formats": ["html", "rawHtml"]})
    return (res.get("html") or "") + "\n" + (res.get("rawHtml") or "")
