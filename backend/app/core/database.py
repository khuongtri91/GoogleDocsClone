from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_engine() -> Engine:
    database_url = get_settings().database_url

    if not database_url:
        raise ConfigurationError("DATABASE_URL is required for document CRUD")

    return create_engine(_normalize_database_url(database_url), pool_pre_ping=True)


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)

    return database_url


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db_session() -> Generator[Session]:
    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()
