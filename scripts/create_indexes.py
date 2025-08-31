"""
scripts/create_indexes.py

Usage:
  python scripts/create_indexes.py <tenant>

Reads MONGO_URI and CORE_DB from .env.
Creates per-tenant collections and indexes for Phase 2.1 acceptance.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_indexes.py <tenant>")
        sys.exit(2)

    tenant = sys.argv[1].strip().lower()
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("CORE_DB")

    if not uri or not db_name:
        print("ERROR: MONGO_URI or CORE_DB missing in environment")
        sys.exit(1)

    client = MongoClient(uri)
    db = client[db_name]

    # Per-tenant collection names (simple convention)
    coll_scans = db[f"{tenant}_scans"]         # Kavach scan results
    coll_costs = db[f"{tenant}_costs"]         # Rudra cost snapshots/forecast IO
    coll_qc    = db[f"{tenant}_qc_results"]    # Trinetra vision QC results
    coll_logs  = db[f"{tenant}_audit_logs"]    # Generic audit/event logs

    # Create indexes (idempotent; PyMongo will skip if they exist)
    # Scans: query by target & created_at, status filters
    scans_indexes = [
        ("by_target_ts",   [("target", ASCENDING), ("created_at", DESCENDING)]),
        ("by_status_ts",   [("status", ASCENDING), ("created_at", DESCENDING)]),
        ("by_ts",          [("created_at", DESCENDING)]),
    ]
    for name, keys in scans_indexes:
        coll_scans.create_index(keys, name=name)

    # Costs: by service, month; recent first
    costs_indexes = [
        ("by_service_month", [("service", ASCENDING), ("month", DESCENDING)]),
        ("by_ts",            [("created_at", DESCENDING)]),
    ]
    for name, keys in costs_indexes:
        coll_costs.create_index(keys, name=name)

    # QC results: by part_id, batch, created_at
    qc_indexes = [
        ("by_part_ts",    [("part_id", ASCENDING), ("created_at", DESCENDING)]),
        ("by_batch_ts",   [("batch_id", ASCENDING), ("created_at", DESCENDING)]),
        ("by_ts",         [("created_at", DESCENDING)]),
    ]
    for name, keys in qc_indexes:
        coll_qc.create_index(keys, name=name)

    # Audit logs: by actor and time, and by event type
    log_indexes = [
        ("by_actor_ts",   [("actor", ASCENDING), ("created_at", DESCENDING)]),
        ("by_event_ts",   [("event", ASCENDING), ("created_at", DESCENDING)]),
        ("by_ts",         [("created_at", DESCENDING)]),
    ]
    for name, keys in log_indexes:
        coll_logs.create_index(keys, name=name)

    print(f"Indexes created for {tenant}")
    # Optional: print actual index names for snapshotting in Atlas UI
    for coll in (coll_scans, coll_costs, coll_qc, coll_logs):
        print(f" - {coll.name}: {[idx['name'] for idx in coll.list_indexes()]}")


if __name__ == "__main__":
    main()
