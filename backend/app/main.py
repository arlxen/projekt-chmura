from fastapi import FastAPI, HTTPException
from typing import List
import uuid
import os

from .schemas import BookmarkIn, BookmarkOut
from .db import engine, init_db, bookmarks
from sqlalchemy import insert, select


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    # check db connectivity
    try:
        with engine.connect() as conn:
            conn.execute(select(1))
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="db unavailable")


@app.post("/bookmarks", response_model=BookmarkOut, status_code=201)
def add_bookmark(b: BookmarkIn):
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "url": str(b.url),
        "status": "pending",
        "title": None,
        "description": None,
    }
    with engine.begin() as conn:
        conn.execute(insert(bookmarks).values(**item))
    return item


@app.get("/bookmarks", response_model=List[BookmarkOut])
def list_bookmarks():
    with engine.connect() as conn:
        rows = conn.execute(select(bookmarks)).all()
    result = [dict(r._mapping) for r in rows]
    return result
