import asyncio

import pytest

from src.config import Settings
from src.database.db import Database


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    settings_test = Settings()
    database_test = Database(db_url=settings_test.database.dsn)
    assert settings_test.database.mode == "TEST"

    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
