from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from promptlab.settings import settings


@lru_cache(maxsize=8)
def _engine_for(url: str):
    return create_engine(url, pool_pre_ping=True)


def get_engine():
    return _engine_for(settings.database_url)


def get_sessionmaker():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
