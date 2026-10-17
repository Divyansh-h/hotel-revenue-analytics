"""
Initializes the target PostgreSQL database hotel_analytics if it does not exist.
Connects to default 'postgres' database with autocommit=True.
"""

import sys
from pathlib import Path
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.db import get_connection, get_db_config


def create_database():
    cfg = get_db_config()
    target_db = cfg["dbname"]

    print(f"Connecting to default 'postgres' database on {cfg['host']}:{cfg['port']}...")
    conn = get_connection(database="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
    exists = cursor.fetchone() is not None

    if exists:
        print(f"Database '{target_db}' already exists. No action taken.")
    else:
        print(f"Creating database '{target_db}'...")
        cursor.execute(f'CREATE DATABASE "{target_db}";')
        print(f"Database '{target_db}' created successfully.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_database()
