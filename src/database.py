from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings import settings

engine = create_async_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
async_session = async_sessionmaker(engine)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
