import os, hashlib
from pymongo import MongoClient, UpdateOne

try:
    import bcrypt
except Exception:
    bcrypt = None

uri = os.environ["MONGO_URI"]
dbn = os.environ["DB_NAME"]
db = MongoClient(uri)[dbn]

def hash_pack(pw: str):
    out = {
        "password": pw,  # some dev stacks keep plain in dev mode
        "password_sha256": hashlib.sha256(pw.encode()).hexdigest(),
    }
    if bcrypt:
        out["password_hash"] = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
        out["hashed_password"] = out["password_hash"]  # common field name
        out["password_bcrypt"] = out["password_hash"]
    return out

def user_variants(user, pw, role, tenant):
    base = {
        "username": user,
        "user": user,
        "email": f"{user}@example.com",
        "role": role,
        "roles": [role],
        "permissions": ["*"],
        "active": True,
        "tenant": tenant,
        "tenant_id": tenant,
        "org": tenant,
        "host": f"{tenant}.lvh.me",
        **hash_pack(pw),
    }
    return [
        base,
        {**base, "status": "active"},
        {**base, "enabled": True},
    ]

def seed_many(users):
    colnames = [
        "users", "tenant1_users", "users_tenant1",
        "accounts", "auth_users", "members"
    ]
    ops = []
    for (user, pw, role, tenant) in users:
        for colname in colnames:
            c = db[colname]
            for doc in user_variants(user, pw, role, tenant):
                for q in [
                    {"username": user, "tenant": tenant},
                    {"user": user, "tenant": tenant},
                    {"email": f"{user}@example.com", "tenant": tenant},
                    {"username": user},
                    {"user": user},
                    {"email": f"{user}@example.com"},
                ]:
                    ops.append(UpdateOne(q, {"$set": doc}, upsert=True))
            # apply in batches per collection
            if ops:
                c.bulk_write(ops, ordered=False)
                ops.clear()

seed_many([
    ("owner", "owner", "owner", "tenant1"),
    ("analyst", "analyst", "analyst", "tenant1"),
])

print("OK: seeded users into collections:", db.list_collection_names())
