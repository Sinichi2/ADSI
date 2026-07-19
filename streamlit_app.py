"""ADSI live demo. Four ingestion paths -> one canonical token JSON + HITL review.

Runs the same `ingestion` modules the CLI uses. Paths needing extra libs/keys
(PDF, Word, website, figma) degrade with a clear message instead of crashing.
"""
import json, os, tempfile

import streamlit as st
from dotenv import load_dotenv
from ingestion import document_agent, figma_agent, hitl_export, manual_wizard, website_agent

load_dotenv()
st.set_page_config(page_title="ADSI — Design System Integration", page_icon="🎨", layout="wide")
st.title("Agentic Design System Integration")
st.caption("Upload / connect / describe a design system → one canonical token schema.")


def _cfg():
    return {
        "firecrawl_key": os.getenv("FIRECRAWL_API_KEY"),
        "google_key": os.getenv("GOOGLE_API_KEY"),
        "figma_token": os.getenv("FIGMA_ACCESS_TOKEN"),
    }


def _show(doc):
    hitl = hitl_export.build(doc)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Canonical tokens")
        st.json(doc)
        st.download_button("Download tokens.json", json.dumps(doc, indent=2),
                           "tokens.json", "application/json")
    with c2:
        st.subheader("HITL review")
        if hitl["review_items"]:
            st.warning(f"{len(hitl['review_items'])} token(s) need review.")
            st.json(hitl)
            st.download_button("Download hitl.json", json.dumps(hitl, indent=2),
                               "hitl.json", "application/json")
        else:
            st.success("No review needed — all tokens confident.")


def _run(fn):
    try:
        _show(fn())
    except Exception as e:  # noqa: BLE001 - surface path errors to the user, don't crash the app
        st.error(f"{type(e).__name__}: {e}")


tab_doc, tab_web, tab_manual = st.tabs(
    ["📄 Document", "🌐 Website", "✏️ Manual"])

with tab_doc:
    st.write("PDF / Word / Excel design spec. Excel needs no keys; PDF-swatch and Word-prose need `GOOGLE_API_KEY`.")
    up = st.file_uploader("Design file", type=["pdf", "docx", "xlsx", "xls"])
    if up and st.button("Extract tokens", key="doc"):
        suffix = os.path.splitext(up.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(up.getbuffer())
            path = tmp.name
        _run(lambda: document_agent.run(path, _cfg()))


# # Uncomment if want to include figma
#     with tab_figma:
#     st.write("Reads Figma local variables. Needs `FIGMA_ACCESS_TOKEN` (or MCP connection).")
#     key = st.text_input("Figma file key")
#     if key and st.button("Pull variables", key="figma"):
#         _run(lambda: figma_agent.run(key, _cfg()))

with tab_web:
    st.write("Scrapes a live site and infers tokens. Needs `FIRECRAWL_API_KEY` (+ `GOOGLE_API_KEY` for naming).")
    url = st.text_input("URL", placeholder="https://example.com")
    thr = st.slider("Confidence threshold", 0.0, 1.0, 0.75, 0.05)
    if url and st.button("Scrape & infer", key="web"):
        cfg = _cfg()
        cfg["confidence_threshold"] = thr
        _run(lambda: website_agent.run(url, cfg))

with tab_manual:
    st.write("Define from scratch. Human is source of truth — all tokens are trusted.")
    st.caption("One `name value` per line, e.g. `blue-500 #3b82f6`.")
    fields = {
        "primitive_color": "Primitive colors", "semantic_color": "Semantic colors",
        "type_scale": "Type scale", "spacing": "Spacing", "radius": "Radius", "shadow": "Shadow",
        }
    payload = {}
    for k, label in fields.items():
        text = st.text_area(label, key=f"m_{k}", height=80)
        entries = {}
        for line in text.splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2:
                entries[parts[0]] = parts[1]
        if entries:
            payload[k] = entries
    if st.button("Build tokens", key="manual"):
        if payload:
            _run(lambda: manual_wizard.build_doc(payload))
        else:
            st.info("Enter at least one token.")
