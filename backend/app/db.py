import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Text,
)

DATABASE_URL = os.getenv("POSTGRES_DSN") or f"sqlite:///./data.db"

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
    metadata.create_all(engine)
