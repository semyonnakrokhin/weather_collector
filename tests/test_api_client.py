import json
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from unittest import mock

import aiohttp
import pytest
from payloads import city_payload_1, city_payload_2, response_data

from src.apiclients.realisations import OpenweathermapByCityAPIClient
from src.exceptions import (
    ApiClientError,
    WeatherDataError,
    WeatherFetchingError,
    WeatherParsingError,
)
from src.models.dto import JsonOpenweathermapResponseDTO


@pytest.mark.parametrize(
    argnames="payload_1, payload_2, res, expectation",
    argvalues=[
        (
            city_payload_1,
            city_payload_2,
            [
                JsonOpenweathermapResponseDTO(**city_payload_1),
                JsonOpenweathermapResponseDTO(**city_payload_2),
            ],
            does_not_raise(),
        )
    ],
)
async def test_get_weather_data_integration(
    payload_1, payload_2, res, expectation, container
):
    city_name_1 = payload_1.get("name")
    city_name_2 = payload_2.get("name")

    weather_client_mock = mock.Mock(spec=OpenweathermapByCityAPIClient)

    def func_process(
        session: aiohttp.ClientSession, city: str, timestamp: datetime
    ) -> JsonOpenweathermapResponseDTO:
        d = {
            city_name_1: JsonOpenweathermapResponseDTO(**payload_1),
            city_name_2: JsonOpenweathermapResponseDTO(**payload_2),
        }
        return d.get(city)

    weather_client_mock.get.side_effect = func_process

    with expectation:
        with container.api_clients.weather_client_provider.override(
            weather_client_mock
        ):
            master_service = container.master.master_service_provider()
            dto_list = await master_service.get_weather_data(
                cities=(city_name_1, city_name_2)
            )

        assert dto_list == res


@pytest.mark.parametrize(
    argnames="payload_1, payload_2, exception, expectation",
    argvalues=[
        (
            city_payload_1,
            city_payload_2,
            WeatherFetchingError(),
            pytest.raises(WeatherFetchingError),
        ),
        (
            city_payload_1,
            city_payload_2,
            WeatherParsingError(),
            pytest.raises(WeatherParsingError),
        ),
        (
            city_payload_1,
            city_payload_2,
            WeatherDataError(),
            pytest.raises(WeatherDataError),
        ),
        (
            city_payload_1,
            city_payload_2,
            ApiClientError(),
            pytest.raises(ApiClientError),
        ),
    ],
)
async def test_get_weather_data_integration_errors(
    payload_1, payload_2, exception, expectation, container
):
    city_name_1 = payload_1.get("name")
    city_name_2 = payload_2.get("name")

    weather_client_mock = mock.Mock(spec=OpenweathermapByCityAPIClient)
    weather_client_mock.get.side_effect = exception

    with expectation:
        with container.api_clients.weather_client_provider.override(
            weather_client_mock
        ):
            master_service = container.master.master_service_provider()
            await master_service.get_weather_data(cities=(city_name_1, city_name_2))


async def test_get_weather_data_success(container):
    api_client = container.api_clients.weather_client_provider()
    http_session_mock = mock.MagicMock(spec=aiohttp.ClientSession)

    city = response_data.get("name")
    timestamp = datetime.now()
    http_session_mock.get.return_value.__aenter__.return_value.text.return_value = (
        json.dumps(response_data)
    )

    result = await api_client.get(http_session_mock, city, timestamp)

    try:
        dto = JsonOpenweathermapResponseDTO(**result)
    except Exception as e:
        assert (
            False
        ), f"Исключение {type(e).__name__} при создании объекта \
        JsonOpenweathermapResponseDTO: {e}"
    else:
        assert True

    assert dto.get("coord") == {"lon": 117.1767, "lat": 39.1422}
    assert dto.get("weather") == [
        {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04n"}
    ]
    assert dto.get("main") == {
        "temp": 268.42,
        "feels_like": 263.37,
        "temp_min": 268.42,
        "temp_max": 268.42,
        "pressure": 1031,
        "humidity": 49,
    }
    assert dto.get("timestamp") == timestamp


# TODO: You need to change import stratagy as pytest look at the one class but
#  with two passes
#  (<class 'src.apiclients.realisations.WeatherFetchingError'>,
#  <class 'apiclients.realisations.WeatherFetchingError'>)
#  as on two different classes
@pytest.mark.parametrize(
    argnames="exception",
    argvalues=[(pytest.raises(ApiClientError), WeatherFetchingError)],
)
async def test_get_weather_data_weather_fetching_error(exception, container):
    api_client = container.api_clients.weather_client_provider()
    http_session_mock = mock.MagicMock(spec=aiohttp.ClientSession)

    city = response_data.get("name")
    timestamp = datetime.now()
    # http_session_mock.get.return_value.__aenter__
    # .return_value.text.return_value = json.dumps(response_data)

    # http_session_mock.get.side_effect = aiohttp.ClientError()

    # with exception:
    #     await api_client.get(http_session_mock, city, timestamp)

    try:
        await api_client.get(http_session_mock, city, timestamp)
        # await my_func()
        # raise WeatherFetchingError()
    except WeatherFetchingError as e:
        print("HHHHHHHHHHHHHHHH")
        print("Тип исключения:", type(e))
        print("Аргументы исключения:", e.args)
        print("Класс исключения:", e.__class__)
        print("Причина исключения:", e.__cause__)
        print("Контекст исключения:", e.__context__)
        print("Трассировка стека:", e.__traceback__)
        print("Документация исключения:", e.__doc__)
    except Exception as e:
        print("dasdasdas")
        print("Тип исключения:", type(e))
        print("Аргументы исключения:", e.args)
        print("Класс исключения:", e.__class__)
        print("Причина исключения:", e.__cause__)
        print("Контекст исключения:", e.__context__)
        print("Трассировка стека:", e.__traceback__)
        print("Документация исключения:", e.__doc__)


async def test_get_weather_data_weather_data_error(container):
    api_client = container.api_clients.weather_client_provider()
    http_session_mock = mock.MagicMock(spec=aiohttp.ClientSession)

    city = response_data.get("name")
    timestamp = 1
    http_session_mock.get.return_value.__aenter__.return_value.text.return_value = (
        json.dumps(response_data)
    )

    with pytest.raises(WeatherDataError):
        await api_client.get(http_session_mock, city, timestamp)
