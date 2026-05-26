from fastapi import FastAPI, HTTPException
from typing import List
import uuid
import os

from .schemas import BookmarkIn, BookmarkOut
from .db import engine, init_db, bookmarks
from sqlalchemy import insert, select
import json

# redis optional
import os
redis_client = None
try:
    import redis as redis_pkg
except Exception:
    redis_pkg = None


app = FastAPI()


@app.get("/")
def root():
    return {"service": "bookmark-manager", "status": "running"}


@app.on_event("startup")
def on_startup():
    init_db()
    # init redis if available
    global redis_client
    redis_url = os.getenv("REDIS_URL")
    if redis_pkg and redis_url:
        try:
            redis_client = redis_pkg.from_url(redis_url)
        except Exception:
            redis_client = None


@app.on_event("shutdown")
def on_shutdown():
    # dispose db engine and close redis
    try:
        engine.dispose()
    except Exception:
        pass
    try:
        if redis_client:
            redis_client.close()
    except Exception:
        pass


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
    # enqueue for worker if redis is configured
    try:
        if redis_client:
            redis_client.rpush("bookmark_queue", json.dumps({"id": item_id, "url": item["url"]}))
    except Exception:
        # don't fail request if redis not available
        pass
    return item


@app.get("/bookmarks", response_model=List[BookmarkOut])
def list_bookmarks():
    with engine.connect() as conn:
        rows = conn.execute(select(bookmarks)).all()
    result = [dict(r._mapping) for r in rows]
    return result
