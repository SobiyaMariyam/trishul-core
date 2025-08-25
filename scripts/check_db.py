from app.db.manager import get_core_db

try:
    db = get_core_db()
    print("Connected OK. Collections:", db.list_collection_names())
except Exception as e:
    print("Connection failed ->", e)
