"""ADSI entry point — multipage nav over the upload and dashboard pages."""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="ADSI — Design System Integration", page_icon="🎨", layout="wide")

pg = st.navigation([
    st.Page("frontend/pages/upload-design-system.py", title="Upload", icon="📥", default=True),
    st.Page("frontend/pages/dashboard.py", title="Dashboard", icon="📊"),
])
pg.run()
