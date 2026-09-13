from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from healthcare_api.core.config import get_settings

settings = get_settings()

# Created at import time (not inside a FastAPI startup hook) so that test
# clients using httpx's ASGITransport - which does not run lifespan events -
# still get a real engine. `main.lifespan` disposes it on shutdown.
engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an async database session per request."""
    async with AsyncSessionLocal() as session:
        yield session
