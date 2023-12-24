import asyncio

import pytest

from src.config import settings
from src.database.db import Base, async_engine


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    assert settings.MODE == "TEST"
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
