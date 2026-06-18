from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings


engine = create_async_engine(settings.DATABASE_URI, echo=False)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def close_engine():
    await engine.dispose()


@asynccontextmanager
async def managed_transaction_async(session_factory: "async_sessionmaker[AsyncSession]"):
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
