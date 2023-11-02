import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self):
        return (
            f"postgresql+asyncpg"
            f"://{self.DB_USER}"
            f":{self.DB_PASS}@{self.DB_HOST}"
            f":{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    )


OPENWEATHERMAP_API_KEY = "a3b4ba7f719f409cbf8a9ebc98fb1511"

settings = Settings()
