# WebGenAI - AI-Powered Multi-Agent Data Engineering Web-browser (Prototype)

Basic prototype for the B.Tech Final Year Project (JSPM University Pune, 2026-27).

## The 4 modules (agents)
| # | Module | File | What it does |
|---|--------|------|--------------|
| 1 | Intent & Planning Agent | `app/agents/planner.py` | Reads the natural-language request, finds URL / table number, builds an execution plan |
| 2 | Web Research & Extraction Agent | `app/agents/web_agent.py` | Fetches an approved page (Requests + BeautifulSoup), extracts HTML tables (or text/links) |
| 3 | Data Cleaning & Transformation Agent | `app/agents/data_agent.py` | Pandas: snake_case columns, remove footnotes, numeric conversion, dedupe, fill missing |
| 4 | Analysis & Validation Agent | `app/agents/analysis_agent.py` | Statistics, insights, correlation, chart data, data-quality score |

Supporting parts: `orchestrator.py` (coordinates agents, retries/errors), `security.py`
(domain allow-list, human approval, audit log -> `logs/audit.log`), `main.py` (FastAPI), `static/index.html` (UI).

Flow: `User -> UI -> Orchestrator -> Planner -> Web Agent -> Data Agent -> Analysis Agent -> Dataset / Insights / Report`

## Run on your laptop (Windows / Linux / Mac)
Requires Python 3.9+.

```bash
cd webgenai
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```
Open **http://127.0.0.1:8000** in your browser and click "Demo: countries (local)" then "Run workflow".

The demo page works offline. Wikipedia and a few other sites are on the allow-list
(`app/config.py`). Any other website triggers a **human approval** prompt.

## Try these requests
- `Collect and analyze the data table from http://127.0.0.1:8000/demo/countries.html`
- `Extract table 2 from https://en.wikipedia.org/wiki/List_of_largest_cities and analyze it`

## Extending (for next phases)
- Replace rule-based `planner.plan()` with an LLM (LangChain / LangGraph).
- Add Playwright to `web_agent.py` for JavaScript-heavy sites.
- Store runs in PostgreSQL; add Docker; add more agents (report writer, API connector).
