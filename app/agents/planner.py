"""MODULE 1 - Intent & Planning Agent.

Converts a natural-language request into a structured, executable plan.
Rule-based (works offline, no API key). Replace `plan()` with an LLM call
(e.g. LangChain/OpenAI/Claude) later without changing the rest of the system.
"""
import re

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)


def plan(request: str) -> dict:
    text = request.strip()
    low = text.lower()

    m = URL_RE.search(text)
    url = m.group(0).rstrip(".,)") if m else None

    # which table on the page? e.g. "table 2"
    tm = re.search(r"table\s*#?(\d+)", low)
    table_index = int(tm.group(1)) - 1 if tm else 0

    opts = {
        "clean": True,  # always clean
        "deduplicate": not any(k in low for k in ["keep duplicates", "no dedup"]),
        "fill_missing": not any(k in low for k in ["keep missing", "no fill"]),
        "analyze": True,
        "report": any(k in low for k in ["report", "summary", "summarize", "insight"]) or True,
    }

    steps = [
        {"agent": "Planner", "task": "Interpret request and build execution plan"},
        {"agent": "WebAgent", "task": f"Fetch and extract data from {url}" if url else "Fetch data"},
        {"agent": "DataAgent", "task": "Clean, normalize and transform dataset"},
        {"agent": "AnalysisAgent", "task": "Analyze data, validate quality, generate report"},
    ]

    return {
        "goal": text,
        "url": url,
        "table_index": max(table_index, 0),
        "options": opts,
        "steps": steps,
        "error": None if url else "No URL found. Include a link, e.g. http://127.0.0.1:8000/demo/countries.html",
    }
