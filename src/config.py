import os
from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


class Settings(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    OPENWEATHERMAP_API_KEY: str

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg"
            f"://{self.DB_USER}"
            f":{self.DB_PASS}@{self.DB_HOST}"
            f":{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(env_file=os.path.join(ROOT_DIR, ".env"))


settings = Settings()

# Выберете имя для файлов
TEXTFILE_NAME = f"meteo_{int(datetime.now().timestamp())}.txt"
JSONFILE_NAME = f"meteo_{int(datetime.now().timestamp())}.json"
# Выберете сервисы для хранения. Возможные варианты:
# ["db", "json", "text"]
SELECTED_STORAGE_SERVICE = ["db", "json", "text"]
# Введите апи-ключ:
OPENWEATHERMAP_API_KEY = settings.OPENWEATHERMAP_API_KEY

di_configuration_dict = {
    "repositories": {
        "textfile_path": os.path.join(ROOT_DIR, "output_text", TEXTFILE_NAME),
        "jsonfile_path": os.path.join(ROOT_DIR, "output_json", JSONFILE_NAME),
    },
    "services": {
        "api_client": {"api_key": OPENWEATHERMAP_API_KEY},
        "storage_services": {"selected_storage_services": SELECTED_STORAGE_SERVICE},
    },
}
