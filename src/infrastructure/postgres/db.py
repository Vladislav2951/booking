from contextlib import asynccontextmanager, contextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# @contextmanager
# def get_sync_db():
#     # For simplicity in tests without docker, allow aiosqlite via env override
#     db_url = settings.DATABASE_URL.replace("+asyncpg", "")
#     local_db_url = (
#         f"sqlite+aiosqlite:///{db_url.split('/')[-1]}"
#         if "localhost" not in db_url
#         else None
#     )

#     url_to_use = local_db_url or db_url
#     sync_engine = (
#         create_async_engine(url_to_use)
#         if "+asyncpg" in settings.DATABASE_URL and aiosqlite.__version__ > ""
#         else engine
#     )
#     # Fallback to standard async session for simplicity across environments
#     yield from get_session()


def get_session():
    return async_session_factory()


async def close_engine():
    await engine.dispose()


@asynccontextmanager
async def managed_transaction(session_factory: "async_sessionmaker[AsyncSession]"):
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
