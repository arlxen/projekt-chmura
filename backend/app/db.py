 import os
from pathlib import Path
from sqlalchemy.engine import URL
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Text,
)
import time
import sqlalchemy

def _read_secret_file(env_name: str) -> str | None:
    secret_path = os.getenv(env_name)
    if not secret_path:
        return None
    try:
        return Path(secret_path).read_text(encoding="utf-8").strip()
    except Exception:
        return None


def _build_database_url() -> str:
    dsn = os.getenv("POSTGRES_DSN")
    if dsn:
        return dsn

    password = os.getenv("POSTGRES_PASSWORD") or _read_secret_file("POSTGRES_PASSWORD_FILE")
    if not password:
        return "sqlite:///./data.db"

    user = os.getenv("POSTGRES_USER", "bookmarks")
    host = os.getenv("POSTGRES_HOST", "db")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    database = os.getenv("POSTGRES_DB", "bookmarks")
    return str(
        URL.create(
            "postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )
    )


DATABASE_URL = _build_database_url()

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

bookmarks = Table(
    "bookmarks",
    metadata,
    Column("id", String, primary_key=True),
    Column("url", Text, nullable=False),
    Column("status", String, nullable=False),
    Column("title", Text, nullable=True),
    Column("description", Text, nullable=True),
)


def init_db():
    # create tables if not exist
    # wait for DB to be ready (useful when running with Postgres in docker)
    try:
        wait_for_db(engine)
    except Exception:
        # if DB not ready after retries, re-raise so service startup fails loudly
        raise
    metadata.create_all(engine)


def wait_for_db(engine, retries: int = 10, delay_seconds: float = 2.0) -> None:
    """Wait for the database to accept connections.

    Tries to connect up to `retries` times, sleeping `delay_seconds`
    between attempts. Raises Exception if not ready.
    """
    last_exc = None
    for _ in range(retries):
        try:
            with engine.connect() as conn:
                return
        except Exception as exc:
            last_exc = exc
            time.sleep(delay_seconds)
    # no successful connection
    raise Exception("DB not ready") from last_exc
