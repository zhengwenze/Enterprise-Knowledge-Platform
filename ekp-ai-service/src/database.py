from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import settings

sync_engine = create_engine(settings.database_url.replace("postgresql://", "postgresql+psycopg2://"))
async_engine = create_async_engine(settings.database_url.replace("postgresql://", "postgresql+asyncpg://"))

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


def get_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
