import os
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from config import settings  # noqa

DB_URL = settings.DB_URL
async_engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
