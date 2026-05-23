from pydantic import BaseModel, HttpUrl
from typing import Optional


class BookmarkIn(BaseModel):
    url: HttpUrl


class BookmarkOut(BaseModel):
    id: str
    url: HttpUrl
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
