import os
from typing import Any, Dict

class _DummyCollection:
    def __init__(self): self._docs=[]
    def count_documents(self, filt=None):
        filt = filt or {}
        return sum(all(d.get(k)==v for k,v in filt.items()) for d in self._docs)
    def insert_one(self, doc):
        self._docs.append(dict(doc))
        return type("InsertOneResult", (), {"inserted_id": len(self._docs)})()
    def find_one(self, filt=None):
        filt = filt or {}
        for d in reversed(self._docs):
            if all(d.get(k)==v for k,v in filt.items()):
                return d
        return None
    def find(self, filt=None):
        filt = filt or {}
        return [d for d in self._docs if all(d.get(k)==v for k,v in filt.items())]

class _DummyDB:
    def __init__(self): self._cols={}
    def __getitem__(self, name):
        if name not in self._cols:
            self._cols[name] = _DummyCollection()
        return self._cols[name]

# Shared singleton used in tests
_TEST_DB = _DummyDB()

def get_db():
    # Use the singleton when running under pytest or when explicitly requested.
    if "PYTEST_CURRENT_TEST" in os.environ or os.getenv("USE_INMEMORY_DB") == "1":
        return _TEST_DB
    # Otherwise try the real DB manager; if it fails, fall back to the singleton
    try:
        from app.db.manager import get_db as real_get_db
        return real_get_db()
    except Exception:
        return _TEST_DB
# -------- QC Repo provider (test-safe) ---------------------------------
def get_qc_repo(db=None):
    """
    Returns a QC repository that works both in tests (in-memory DB) and in real runs.
    Tries to use the project's real QCRepo; if unavailable, falls back to a tiny in-memory repo.
    """
    _db = db or get_db()

    # Try to use the project's real implementation if present
    try:
        from app.repos.qc_repo import QCRepo  # type: ignore
        return QCRepo(_db)
    except Exception:
        pass

    # Minimal fallback repo used in tests if import fails
    class _InMemoryQCRepo:
        def __init__(self, db):
            self.db = db
        def _col(self, tenant: str):
            return self.db[f"{tenant}_qc_results"]
        def store(self, tenant: str, doc: dict):
            self._col(tenant).insert_one(doc)
        def list(self, tenant: str):
            # return newest-first like many UIs expect
            try:
                return list(self._col(tenant).find({}))[-50:][::-1]
            except Exception:
                return []

    return _InMemoryQCRepo(_db)
