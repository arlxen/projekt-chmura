import os
import json
import time
import re
import requests

from sqlalchemy import update

from backend.app.db import engine, bookmarks

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    if m:
        return m.group(1).strip()
    return None


def process_message(msg: str):
    try:
        payload = json.loads(msg)
        bid = payload.get("id")
        url = payload.get("url")
        if not bid or not url:
            return
        # fetch page
        try:
            r = requests.get(url, timeout=10)
            title = extract_title(r.text)
            status = "done"
        except Exception:
            title = None
            status = "error"

        # update db
        with engine.begin() as conn:
            conn.execute(
                update(bookmarks).where(bookmarks.c.id == bid).values(title=title, status=status)
            )
    except Exception:
        return


def run():
    r = redis.from_url(REDIS_URL)
    print("worker connected to redis")
    import signal

    running = True

    def handle_sig(signum, frame):
        nonlocal running
        print("worker: received signal, shutting down")
        running = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    while running:
        try:
            item = r.blpop("bookmark_queue", timeout=5)
            if not item:
                continue
            _, payload = item
            # payload bytes -> decode
            if isinstance(payload, bytes):
                payload = payload.decode()
            process_message(payload)
        except Exception as e:
            print("worker error:", e)
            time.sleep(1)
    # clean shutdown
    try:
        r.close()
    except Exception:
        pass
    print("worker stopped")


if __name__ == "__main__":
    run()
