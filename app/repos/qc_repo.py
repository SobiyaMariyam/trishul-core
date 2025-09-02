from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any

class QCRepo:
    def store(self, tenant: str, doc: Dict[str, Any]) -> None: ...
    def list(self, tenant: str) -> List[Dict[str, Any]]: ...

class InMemoryQCRepo(QCRepo):
    def __init__(self):
        self._store: Dict[str, List[Dict[str, Any]]] = {}

    def store(self, tenant: str, doc: Dict[str, Any]) -> None:
        self._store.setdefault(tenant, []).append(doc)

    def list(self, tenant: str) -> List[Dict[str, Any]]:
        return list(self._store.get(tenant, []))

class MongoQCRepo(QCRepo):
    def __init__(self, db):
        self.db = db

    def _col(self, tenant: str):
        # per-tenant collection; alternatively: use one collection with a tenant field
        return self.db[f"{tenant}_qc_results"]

    def store(self, tenant: str, doc: Dict[str, Any]) -> None:
        self._col(tenant).insert_one(doc)

    def list(self, tenant: str) -> List[Dict[str, Any]]:
        return list(self._col(tenant).find({}))
