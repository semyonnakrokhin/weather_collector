import os
from pprint import pprint

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiClient(BaseModel):
    api_key: str


class ApiClients(BaseModel):
    weather_client: ApiClient


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


class DotenvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    api_clients: ApiClients
    database: Database


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )
    env_filepath = os.path.join(ROOT_DIR, ".env")
    dotenv_settings = DotenvSettings(_env_file=env_filepath)
    pprint(dotenv_settings.model_dump())
