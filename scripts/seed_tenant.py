from app.db.manager import get_core_db
core = get_core_db()
core.tenants.update_one(
    {"slug":"tenant1"},
    {"":{"slug":"tenant1","name":"Tenant One Pvt Ltd","status":"active","plan":"free"}},
    upsert=True
)
print("Upserted tenant1")
