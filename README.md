## ADSI — Agentic Design System Integration
#### **By Shiva Matthew Cruz**

Four ingestion paths — **document**, **figma**, **website**, **manual** — that all converge
on one canonical design-token JSON (`schemas/design-tokens.schema.json`) with per-token
confidence + HITL review metadata.

### Setup
```bash
python -m venv .venv && .venv/Scripts/activate      # or source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                # fill in only the keys you need
```

### Run the live app (Streamlit)
```bash
streamlit run streamlit_app.py
```
Tabs for all four paths; downloads `tokens.json` and, when tokens need review, `hitl.json`.

### Run the CLI
```bash
python main.py document --file ./spec.xlsx --output ./output/tokens.json
python main.py figma    --file-key <key>   --output ./output/tokens.json
python main.py website  --url https://example.com --output ./output/tokens.json --confidence-threshold 0.75
python main.py manual   --output ./output/tokens.json
```

### Credentials per path
| Path | Needs |
|---|---|
| **document** — Excel | nothing |
| **document** — PDF tables | nothing (`pdfplumber`/`camelot`) |
| **document** — PDF swatches / Word prose | `GOOGLE_API_KEY` (Gemini) |
| **manual** | nothing |
| **website** | `FIRECRAWL_API_KEY` (+ `GOOGLE_API_KEY` for semantic naming) |
| **figma** | `FIGMA_ACCESS_TOKEN` (or a connected Figma MCP) |

Heavy libs (camelot, firecrawl, langchain) are **lazy-imported** — the app and the
key-free paths run before you install them. A path that needs a missing lib/key fails
with a clear message instead of crashing.

> The Gemini model string (`GEMINI_MODEL`) defaults to a placeholder — verify the real
> one in Google AI Studio before relying on LLM steps.

### Tests
```bash
pytest -q
```
External APIs (Firecrawl, Gemini, Figma) are not called in tests — deterministic logic
(schema validation, figma mapping, excel parsing, website clustering) is covered with fixtures.

### Out of scope
Figma write-back, the HITL review UI itself (only the export payload), and cross-source
token reconciliation — single-source runs only.
