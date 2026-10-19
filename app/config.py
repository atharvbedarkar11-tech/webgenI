"""Central configuration for WebGenAI prototype."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Domains the agents may visit without human approval (security policy).
# Add your own domains here, or set env var WEBGENAI_ALLOWED="a.com,b.org"
DEFAULT_ALLOWED = [
    "localhost",
    "127.0.0.1",
    "wikipedia.org",
    "books.toscrape.com",
    "quotes.toscrape.com",
]
ALLOWED_DOMAINS = [
    d.strip().lower()
    for d in os.getenv("WEBGENAI_ALLOWED", ",".join(DEFAULT_ALLOWED)).split(",")
    if d.strip()
]

REQUEST_TIMEOUT = 15
USER_AGENT = "WebGenAI-Prototype/0.1 (student project)"
MAX_ROWS = 5000
