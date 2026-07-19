"""PDF table extraction: camelot first, pdfplumber fallback. Both lazy-imported."""

def extract_tables(path):
    """Return a list of tables, each a list-of-rows (list of str). Empty if none found."""
    tables = _camelot(path)
    if tables:
        return tables
    return _pdfplumber(path)

def _camelot(path):
    try:
        import camelot
    except ImportError:
        return []
    try:
        found = camelot.read_pdf(path, pages="all")
        return [t.df.values.tolist() for t in found]
    except Exception:  # noqa: BLE001 - ghostscript/backend issues -> fall through
        return []


def _pdfplumber(path):
    try:
        import pdfplumber
    except ImportError:
        return []
    out = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for tbl in page.extract_tables() or []:
                out.append([[c or "" for c in row] for row in tbl])
    return out


def extract_text(path):
    """All page text, for prose/swatch fallback."""
    try:
        import pdfplumber
    except ImportError as e:
        raise RuntimeError("pip install pdfplumber") from e
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)
