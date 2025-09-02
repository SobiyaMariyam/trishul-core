import os
from typing import Optional
from pymongo import MongoClient

_client: Optional[MongoClient] = None
_db = None

def get_db():
    """
    Lazy singleton DB handle.
    Uses MONGO_URI (or mongodb://localhost:27017), DB_NAME=trishul by default.
    """
    global _client, _db
    if _db is not None:
        return _db
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "trishul")
    # instantiate lazily, at first call (NOT at import)
    _client = MongoClient(uri)
    _db = _client[db_name]
    return _db
