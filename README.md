## ADSI — Agentic Design System Integration
#### **By Shiva Matthew Cruz**

Two ingestion paths: **document**, **website** - all converge on one canonical design-token JSON (`schemas/design-tokens.schema.json`) with per-token confidence + HITL review metadata.

### Setup
To setup, 
```bash
python -m venv .venv && .venv/Scripts/activate      # or source .venv/bin/activate
pip install -r requirements.txt
```

### Run the live app (Streamlit)
```bash
streamlit run streamlit_app.py
```

### Credentials 
Go to the following to get these credentials: 
1. GOOGLE_API_KEY: https://aistudio.google.com/
2. FIRECRAWL_API_KEY: https://www.firecrawl.dev/
3. GEMINI_MODEL: Set to default 

<!-- Soon to be add -->
1. **figma** - Upload your .fig file 
2. **Manual** - Manual integration. 