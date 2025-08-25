"""Database manager utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pymongo import MongoClient

# ---- Load .env manually (robust against UTF-8 BOM / encoding issues) ----
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # .../trishul
ENV_PATH = PROJECT_ROOT / ".env"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        text = path.read_text(encoding="utf-8-sig")  # strips BOM if present
    except Exception:
        text = path.read_text(errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'").strip('"'))


# Load it BEFORE reading any env vars
_load_env_file(ENV_PATH)

# ---- Config ----
CORE_DB = os.getenv("CORE_DB", "trishul_core")

# ---- Lazy client (do not connect at import time) ----
_client: Optional[MongoClient] = None


def _get_client() -> MongoClient:
    """Create or return a singleton MongoClient when first needed."""
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI is not set; define it in env or .env.")
        _client = MongoClient(uri)
    return _client


def get_core_db():
    return _get_client()[CORE_DB]


def get_tenant_db(tenant_slug: str):
    return _get_client()[f"tenant_{tenant_slug}"]
