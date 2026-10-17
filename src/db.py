"""
Database Connection Helpers
Provides get_engine() and get_connection() using credentials from .env.
No hardcoded credentials; adheres to Rule R7.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Find and load .env from project root
REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")


def get_db_config(database: Optional[str] = None) -> dict:
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    dbname = database or os.getenv("PGDATABASE", "hotel_analytics")

    if not user:
        raise ValueError("PGUSER is not set in .env")

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password or "",
        "dbname": dbname
    }


def get_engine(database: Optional[str] = None) -> Engine:
    """
    Returns an SQLAlchemy Engine connected via psycopg2.
    """
    cfg = get_db_config(database)
    auth = f"{cfg['user']}:{cfg['password']}" if cfg["password"] else cfg["user"]
    url = f"postgresql+psycopg2://{auth}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}"
    return create_engine(url)


def get_connection(database: Optional[str] = None):
    """
    Returns a native psycopg2 connection.
    """
    cfg = get_db_config(database)
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"] or None,
        dbname=cfg["dbname"]
    )
