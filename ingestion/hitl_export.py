"""Shared HITL review payload — one format for all four sources."""
from ingestion.schema_assembler import iter_tokens


def build(doc):
    """Collect every `pending` token into a reviewer-facing payload (source-agnostic)."""
    items = []
    for path, tok in iter_tokens(doc):
        if tok.get("hitl_status") != "pending":
            continue
        items.append({
            "token_path": path,
            "type": tok.get("type"),
            "inferred_value": tok.get("value"),
            "confidence": tok.get("confidence"),
            "evidence": tok.get("provenance"),  # screenshot/page/cell/alias chain, whatever the path had
        })
    meta = doc.get("$meta", {})
    return {
        "source_type": meta.get("source_type"),
        "source_ref": meta.get("source_ref"),
        "extracted_at": meta.get("extracted_at"),
        "review_items": items,
    }
