from typing import Type

from aiohttp import ClientSession

from apiclient.services import APIClientService, OpenweathermapByCityAPIClient
from mappers import AbstractControllerMapper, WeatherMapper
from schemas import JsonOpenweathermapResponse, Weather
from storage.repositories import (
    HistoryRecordFileRepository,
    HistoryRecordJSONRepository,
    WeatherRepository,
)
from storage.services import FileService, StorageService, WeatherServiceDB


def get_api_client_service(
    session_http: ClientSession, api_key: str
) -> APIClientService:
    return OpenweathermapByCityAPIClient(session=session_http, api_key=api_key)


def get_response_storage_mapper() -> (
    Type[AbstractControllerMapper[JsonOpenweathermapResponse, Weather]]
):
    return WeatherMapper


def get_weather_db_service() -> StorageService:
    return WeatherServiceDB(repository=WeatherRepository)


def get_textfile_storage_service() -> StorageService:
    return FileService(repository=HistoryRecordFileRepository(filepath="results.txt"))


def get_json_storage_service() -> StorageService:
    return FileService(repository=HistoryRecordJSONRepository(filepath="meteo.json"))


# di_container = punq.Container()
#
# di_container.register(AbstractControllerMapper, WeatherMapper)
# di_container.register(APIClientService, factory=get_api_client_service)
# di_container.register(StorageService, factory=get_weather_db_service)
