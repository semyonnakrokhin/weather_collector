import asyncio

import pytest

from src.database.db import Database
from src.main import create_app_container, get_config_dict


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    settings_test = get_config_dict()
    database_test = Database(db_url=settings_test.get("database").get("dsn"))
    assert settings_test.get("database").get("mode") == "TEST"

    await database_test.delete_and_create_database()


@pytest.fixture(scope="session")
def settings_dict():
    return get_config_dict()


@pytest.fixture(scope="session")
def container(settings_dict):
    app_container = create_app_container(config_dict=settings_dict)
    return app_container


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
