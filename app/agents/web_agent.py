"""MODULE 2 - Web Research & Extraction Agent.

Fetches an approved web page and extracts structured data:
  1. HTML tables  -> DataFrame (preferred)
  2. fallback     -> headings / links / paragraphs as a DataFrame
"""
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

from ..config import MAX_ROWS, REQUEST_TIMEOUT, USER_AGENT


def fetch_html(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.text


def extract(url: str, table_index: int = 0) -> dict:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.get_text(strip=True) if soup.title else url

    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        tables = []

    if tables:
        idx = min(table_index, len(tables) - 1)
        df = tables[idx]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(str(c) for c in col if "Unnamed" not in str(c)).strip() for col in df.columns]
        return {
            "df": df.head(MAX_ROWS),
            "mode": "table",
            "title": title,
            "note": f"Found {len(tables)} table(s); using table {idx + 1}.",
        }

    # Fallback: semi-structured extraction
    rows = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "a"]):
        txt = tag.get_text(" ", strip=True)
        if not txt:
            continue
        rows.append({"type": tag.name, "text": txt, "href": tag.get("href", "") if tag.name == "a" else ""})
    df = pd.DataFrame(rows).head(MAX_ROWS)
    return {"df": df, "mode": "text", "title": title, "note": "No tables found; extracted headings, paragraphs and links."}
