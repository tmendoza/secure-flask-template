#!/usr/bin/env python3
import os
import sys

# ─── ensure project root is on sys.path ────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# ─── now imports will work ─────────────────────────────────────────────────
from app.db import get_connection

def run_migrations():
    conn = get_connection()
    with conn.cursor() as cur:
        # open the init SQL from migrations/
        sql_file = os.path.join(project_root, "migrations", "init.sql")
        with open(sql_file, "r") as f:
            cur.execute(f.read())
    conn.commit()

if __name__ == "__main__":
    run_migrations()
