"""Security & Audit module: domain allow-list + execution logging."""
import json
from datetime import datetime
from urllib.parse import urlparse

from .config import ALLOWED_DOMAINS, LOG_DIR


def is_allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)


class AuditLog:
    """Records every agent action; shown in the UI and saved to logs/audit.log."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.entries = []

    def add(self, agent: str, message: str, status: str = "ok"):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "status": status,
            "message": message,
        }
        self.entries.append(entry)
        with open(LOG_DIR / "audit.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({"run": self.run_id, **entry}) + "\n")
