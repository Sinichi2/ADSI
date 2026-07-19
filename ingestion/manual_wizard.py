"""Manual path: human is the source of truth -> all tokens confidence 1.0.

`build_groups` is headless (reused by both the CLI wizard and the Streamlit form).
`run` is the interactive CLI wizard with resumable JSON draft.
"""
import json
import logging
import os

from ingestion import llm
from ingestion.schema_assembler import assemble, make_token

log = logging.getLogger(__name__)

# payload key -> (schema path, token type)
_SECTIONS = {
    "primitive_color": (("color", "primitive"), "color"),
    "semantic_color": (("color", "semantic"), "color"),
    "type_scale": (("typography", "fontSize"), "fontSize"),
    "spacing": (("spacing",), "dimension"),
    "radius": (("radius",), "dimension"),
    "shadow": (("shadow",), "shadow"),
}


def build_groups(payload):
    """payload = {section: {token_name: value}} -> schema token groups (all conf 1.0)."""
    groups = {}
    for section, (path, ttype) in _SECTIONS.items():
        entries = payload.get(section) or {}
        if not entries:
            continue
        node = groups
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = {name: make_token(str(val), ttype, confidence=1.0)
                          for name, val in entries.items()}
    return groups


def build_doc(payload, source_ref="manual-entry"):
    return assemble("manual", source_ref, build_groups(payload))


def suggest_scale(seeds, kind="spacing", api_key=None):
    """Optional Gemini assist: propose a full scale from a couple of seed values.
    Returns {} if no LLM — caller falls back to manual entry. Never auto-applied.
    """
    if not llm.available():
        return {}
    try:
        raw = llm.call(
            f"Given seed {kind} values {seeds}, propose a coherent {kind} scale as "
            'JSON {name: value}. 6-8 steps.', api_key=api_key)
        import re
        m = re.search(r"\{.*\}", raw, re.S)
        return json.loads(m.group(0)) if m else {}
    except (llm.LLMUnavailable, json.JSONDecodeError):
        return {}


# --- interactive CLI --------------------------------------------------------
def run(config=None, draft_path=".manual_draft.json"):
    config = config or {}
    payload = _load_draft(draft_path)
    print("Manual design-system setup. Blank line ends a section. Progress auto-saved.\n")
    for section in _SECTIONS:
        if payload.get(section):
            print(f"[{section}] resumed with {len(payload[section])} entries — enter to keep.")
        print(f"-- {section.replace('_', ' ')} -- (name value):")
        entries = dict(payload.get(section, {}))
        while True:
            line = input("  ").strip()
            if not line:
                break
            parts = line.split(None, 1)
            if len(parts) == 2:
                entries[parts[0]] = parts[1]
        payload[section] = entries
        _save_draft(draft_path, payload)
    doc = build_doc(payload, source_ref=config.get("source_ref", "manual-entry"))
    if os.path.exists(draft_path):
        os.remove(draft_path)
    return doc


def _load_draft(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_draft(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
