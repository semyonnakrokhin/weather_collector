import os
import sys

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from units_of_work.abstractions import BaseUnitOfWork  # noqa
from repositories.realisations import WeatherDatabaseRepository  # noqa


class WeatherUnitOfWork(BaseUnitOfWork):
    allowed_repository_classes = [WeatherDatabaseRepository]

    async def __aenter__(self):
        """
        Async context manager entry method.

        Calls the base class entry method and retrieves the WeatherDatabaseRepository instance.
        """
        await super().__aenter__()
        self.weather_database_repository = self.get_repository(repository_class=WeatherDatabaseRepository)
