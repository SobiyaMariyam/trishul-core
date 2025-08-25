import os
from pathlib import Path

from typing import Optional
from pymongo.mongo_client import MongoClient

_client: Optional[MongoClient] = MongoClient(MONGO_URI) if MONGO_URI else None

# ---- Load .env manually (robust against UTF-8 BOM / encoding issues) ----
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # ...\trishul
ENV_PATH = PROJECT_ROOT / ".env"


def _load_env_file(path: Path):
    if not path.exists():
        return
    try:
        text = path.read_text(encoding="utf-8-sig")
    except Exception:
        # fallback if encoding is weird
        text = path.read_text(errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'").strip('"')  # remove accidental quotes
            os.environ.setdefault(k, v)


# Load it before reading any env vars
_load_env_file(ENV_PATH)

# ---- Config ----
CORE_DB = os.getenv("CORE_DB", "trishul_core")
MONGO_URI = os.getenv("MONGO_URI")

# ---- Client ----
_client = MongoClient(MONGO_URI) if MONGO_URI else None


def get_core_db():
    if not _client:
        raise RuntimeError("MONGO_URI not set. Create .env with MONGO_URI.")
    return _client[CORE_DB]


def get_tenant_db(tenant_slug: str):
    if not _client:
        raise RuntimeError("MONGO_URI not set. Create .env with MONGO_URI.")
    return _client[f"tenant_{tenant_slug}"]
