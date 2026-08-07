"""Visual preview of the last extracted design system (populated by the Upload page)."""
import streamlit as st
from ingestion import hitl_export
from ingestion.schema_assembler import iter_tokens

st.title("Design System Dashboard")
st.caption("Rendered preview of the last canonical token set.")

doc = st.session_state.get("tokens_doc")
if not doc:
    st.info("No tokens extracted yet — run an extraction first.")
    st.page_link("frontend/pages/upload-design-system.py", label="Go to Upload", icon="📥")
    st.stop()

meta = doc.get("$meta", {})
st.caption(f"Source: {meta.get('source_type')} · {meta.get('source_ref')} · {meta.get('extracted_at')}")

groups = {}
for path, tok in iter_tokens(doc):
    groups.setdefault(path.split(".")[0], []).append((path, tok))

if "color" in groups:
    st.subheader("Colors")
    cols = st.columns(6)
    for i, (path, tok) in enumerate(groups["color"]):
        with cols[i % 6]:
            st.markdown(
                f"<div style='height:48px;border-radius:6px;background:{tok['value']};"
                "border:1px solid rgba(128,128,128,.3)'></div>",
                unsafe_allow_html=True,
            )
            st.caption(f"{path}\n\n{tok['value']}")

if "typography" in groups:
    st.subheader("Typography")
    for path, tok in groups["typography"]:
        st.markdown(f"<span style='font-size:{tok['value']}'>{path} — {tok['value']}</span>",
                    unsafe_allow_html=True)

if "spacing" in groups:
    st.subheader("Spacing")
    for path, tok in groups["spacing"]:
        st.markdown(f"**{path}**: {tok['value']}")
        st.markdown(f"<div style='height:10px;width:{tok['value']};background:#888;border-radius:2px'></div>",
                    unsafe_allow_html=True)

if "radius" in groups:
    st.subheader("Radius")
    cols = st.columns(len(groups["radius"]))
    for col, (path, tok) in zip(cols, groups["radius"]):
        with col:
            st.markdown(
                f"<div style='width:64px;height:64px;background:#3b82f6;border-radius:{tok['value']}'></div>",
                unsafe_allow_html=True,
            )
            st.caption(f"{path}: {tok['value']}")

if "shadow" in groups:
    st.subheader("Shadows")
    cols = st.columns(len(groups["shadow"]))
    for col, (path, tok) in zip(cols, groups["shadow"]):
        with col:
            st.markdown(
                f"<div style='width:96px;height:64px;background:#fff;border-radius:8px;"
                f"box-shadow:{tok['value']}'></div>",
                unsafe_allow_html=True,
            )
            st.caption(path)

if "logo" in groups or "icon" in groups:
    st.subheader("Logo / Icon")
    assets = groups.get("logo", []) + groups.get("icon", [])
    cols = st.columns(len(assets))
    for col, (path, tok) in zip(cols, assets):
        with col:
            try:
                st.image(tok["value"], width=96)
            except Exception:  # noqa: BLE001 - unreachable URL/path, fall back to showing the value
                st.caption("(preview unavailable)")
            st.caption(f"{path}: {tok['value']}")

if "brand_guide" in groups or "principles" in groups:
    st.subheader("Brand Guide / Principles")
    for path, tok in groups.get("brand_guide", []) + groups.get("principles", []):
        st.markdown(f"> **{path}** — {tok['value']}")

hitl = hitl_export.build(doc)
if hitl["review_items"]:
    st.warning(f"{len(hitl['review_items'])} token(s) need review.")

with st.expander("Raw JSON"):
    st.json(doc)
