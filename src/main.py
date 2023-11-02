import asyncio
from datetime import datetime

import aiohttp
from aiohttp import ClientSession

import config
from apiclient.controllers import controller_openweathermapapi
from dependencies import (
    get_api_client_service,
    get_json_storage_service,
    get_response_storage_mapper,
    get_textfile_storage_service,
    get_weather_db_service,
)
from storage.controllers import controller_storage
from top_cities import cities_tuple


async def process_city(session_http: ClientSession, city: str, timestamp: datetime):
    """
    Application unit gathering all services with controllers responsible for:
    - collecting meteo data in a city from another service
    - transforming data
    - saving data in a storage
    :param session_http: aiohttp session in which request will be send
    :param city: city in which we want to collect data
    :param timestamp: time moment in which we look meteo data
    :return: None
    """

    api_key = config.OPENWEATHERMAP_API_KEY

    weather_api_data_dict = await controller_openweathermapapi(
        api_client=get_api_client_service(session_http, api_key),
        city=city,
        timestamp=timestamp,
    )
    weather = get_response_storage_mapper().to_target(source_obj=weather_api_data_dict)
    await controller_storage(storage_service=get_weather_db_service(), weather=weather)
    await controller_storage(
        storage_service=get_textfile_storage_service(), weather=weather
    )
    await controller_storage(
        storage_service=get_json_storage_service(), weather=weather
    )


async def main():
    timestamp = datetime.utcnow()

    async with aiohttp.ClientSession() as session_http:
        for city in cities_tuple:
            await process_city(
                session_http=session_http, city=city, timestamp=timestamp
            )


if __name__ == "__main__":
    asyncio.run(main())
