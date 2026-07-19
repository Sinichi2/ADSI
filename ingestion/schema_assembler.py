"""Shared schema assembly + validation. All four paths funnel through here."""
import json
import logging
import os
from datetime import datetime, timezone

import jsonschema

log = logging.getLogger(__name__)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "design-tokens.schema.json")
AGENT_VERSION = "0.1.0"
DEFAULT_THRESHOLD = 0.75

# Top-level token category keys in the schema (everything else under a path is nesting).
_CATEGORY_KEYS = {"color", "typography", "spacing", "radius", "shadow"}


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def hitl_status_for(confidence, threshold=DEFAULT_THRESHOLD):
    """Confidence gate shared by document-prose, swatch, and website paths."""
    return "not_required" if confidence >= threshold else "pending"


def make_token(value, ttype, confidence=1.0, threshold=DEFAULT_THRESHOLD,
               description=None, provenance=None, hitl_status=None):
    """Build one schema-shaped token. hitl_status auto-derives from confidence unless forced."""
    if hitl_status is None:
        hitl_status = hitl_status_for(confidence, threshold)
    tok = {"value": value, "type": ttype,
           "confidence": round(float(confidence), 3), "hitl_status": hitl_status}
    if description:
        tok["description"] = description
    if provenance:
        tok["provenance"] = provenance
    return tok


def iter_tokens(doc, _prefix=""):
    """Yield (dotted_path, token_dict) for every leaf token, skipping $meta."""
    for key, val in doc.items():
        if key == "$meta" or not isinstance(val, dict):
            continue
        path = f"{_prefix}{key}"
        if "value" in val and "type" in val:
            yield path, val
        else:
            yield from iter_tokens(val, _prefix=f"{path}.")


def assemble(source_type, source_ref, groups, modes=None):
    """Wrap token groups in $meta, set requires_hitl, validate (one retry), return doc."""
    doc = {"$meta": {
        "source_type": source_type,
        "source_ref": source_ref,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "extraction_agent_version": AGENT_VERSION,
    }}
    doc.update({k: v for k, v in groups.items() if v})
    doc["$meta"]["requires_hitl"] = any(
        t.get("hitl_status") == "pending" for _, t in iter_tokens(doc))
    if modes and len(modes) > 1:
        doc["$meta"]["modes"] = modes

    schema = load_schema()
    for attempt in (1, 2):
        try:
            jsonschema.validate(doc, schema)
            return doc
        except jsonschema.ValidationError as e:
            log.error("schema validation failed at %s: %s", list(e.absolute_path), e.message)
            if attempt == 2:
                raise
    return doc
