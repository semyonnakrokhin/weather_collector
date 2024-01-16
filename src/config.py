import os
from datetime import datetime
from pprint import pprint
from typing import List

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Configuration Module

This module provides a configuration structure for the weather collector application.
The configuration includes settings for API clients, database connection,
file repositories,and storage services.

Example Configuration Structure:
{
    'api_clients': {
        'weather_client': {
            'api_key': 'your_api_key_here'
        }
    },
    'database': {
        'db_host': 'localhost',
        'db_name': 'your_database_name',
        'db_pass': 'your_database_password',
        'db_port': 'your_database_port',
        'db_user': 'your_database_user',
        'dsn': 'your_database_dsn',
        'mode': 'your_application_mode'
    },
    'repositories': {
        'json_repo': {
            'filepath': 'path_to_json_file'
        },
        'text_repo': {
            'filepath': 'path_to_text_file'
        }
    },
    'storage_services': {
        'selected_storage_services': ['db', 'json', 'text']
    }
}
"""

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
env_filepath = os.path.join(ROOT_DIR, ".env")
allowed_storage_services_designations = ("db", "text", "json")


class ApiClient(BaseModel):
    api_key: str


class ApiClients(BaseModel):
    weather_client: ApiClient


class StorageServices(BaseModel):
    selected_storage_services: str

    @field_validator("selected_storage_services")
    def parse_to_list(cls, v: str) -> List[str]:
        return v.split(",")


class Repository(BaseModel):
    model_config = SettingsConfigDict(extra="allow")

    directory: str

    def __init__(self, **data):
        super().__init__(**data)
        self.filepath = self._filepath_constructor()
        del self.directory

    def _filepath_constructor(self) -> str:
        return self._get_filepath(self.directory)

    # class Config:
    #     extra = "allow"


class TextfileRepository(Repository):
    @staticmethod
    def _get_filepath(directory: str) -> str:
        filename = f"meteo_{int(datetime.now().timestamp() * 1e6)}.txt"
        return os.path.join(ROOT_DIR, directory, filename)


class JsonRepository(Repository):
    @staticmethod
    def _get_filepath(directory: str) -> str:
        filename = f"meteo_{int(datetime.now().timestamp() * 1e6)}.json"
        return os.path.join(ROOT_DIR, directory, filename)


class Repositories(BaseModel):
    text_repo: TextfileRepository
    json_repo: JsonRepository


class Database(BaseModel):
    model_config = SettingsConfigDict(extra="allow")

    mode: str
    db_host: str
    db_port: str
    db_user: str
    db_pass: str
    db_name: str

    def __init__(self, **data):
        super().__init__(**data)
        self.dsn = self.async_postgres_dsn

    @property
    def async_postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg"
            f"://{self.db_user}"
            f":{self.db_pass}@{self.db_host}"
            f":{self.db_port}/{self.db_name}"
        )

    # class Config:
    #     extra = "allow"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_filepath,
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    api_clients: ApiClients
    storage_services: StorageServices
    repositories: Repositories
    database: Database

    # class Config:
    #     env_file = env_filepath
    #     env_nested_delimiter = '__'
    #     case_sensitive = False
    #     extra = "ignore"


if __name__ == "__main__":
    settings = Settings()
    pprint(settings.model_dump())
