from datetime import date, datetime, time
from enum import Enum
from pprint import pprint
from typing import TypeAlias, TypedDict

from pydantic import BaseModel


class JsonOpenweathermapResponse(TypedDict):
    coord: dict
    weather: list[dict]
    base: str
    main: dict
    visibility: int
    wind: dict
    rain: dict
    clouds: dict
    dt: int
    sys: dict
    timezone: int
    id: int
    name: str
    cod: int
    timestamp: datetime


class WeatherTypeOpenweathermap(str, Enum):
    THUNDERSTORM = "Гроза"
    DRIZZLE = "Изморось"
    RAIN = "Дождь"
    SNOW = "Снег"
    MIST = "Туманная дымка"
    SMOKE = "Копоть"
    HAZE = "Мгла"
    DUST = "Пыль"
    FOG = "Туман"
    SAND = "Песок"
    ASH = "Пепел"
    SQUALL = "Шквал"
    TORNADO = "Торнадо"
    CLEAR = "Ясно"
    CLOUDS = "Облачно"


Celsius: TypeAlias = int


class Weather(BaseModel):
    timestamp: datetime
    city: str
    temperature: Celsius
    weather_type: WeatherTypeOpenweathermap
    sunrise: time
    sunset: time


class HistoryRecord(BaseModel):
    timestamp: datetime
    city: str
    temperature: Celsius
    weather_type: WeatherTypeOpenweathermap
    sunrise: time
    sunset: time

    def __str__(self):
        DATE_FORMAT = "%d.%m.%Y"
        TIME_FORMAT = "%H:%M"

        return (
            f"Date: {self.timestamp.date().strftime(DATE_FORMAT)}\n"
            f"Time: {self.timestamp.time().strftime(TIME_FORMAT)} UTC\n"
            f"City: {self.city}\n"
            f"Temperature: {self.temperature} °C\n"
            f"Weather type: {self.weather_type.value}\n"
            f"Sunrise: {self.sunrise.strftime(TIME_FORMAT)} UTC\n"
            f"Sunset: {self.sunset.strftime(TIME_FORMAT)} UTC\n"
        )

    @staticmethod
    def str2dict(data_str: str) -> dict:
        lines = data_str.strip().split("\n")

        timestamp_value = {}
        payload = {}
        for line in lines:
            _key, _value = line.split(": ")
            __value, *_ = _value.split()

            if _key in ("Date", "Time"):
                timestamp_value[_key.lower()] = __value
                continue

            if _key == "Weather type":
                _key = "_".join(_key.split())

            try:
                __value = Celsius(__value)
            except ValueError:
                pass

            try:
                __value = WeatherTypeOpenweathermap(__value)
            except ValueError:
                pass

            payload[_key.lower()] = __value

        date_obj = date(*map(int, timestamp_value["date"].split(".")[::-1]))
        time_obj = time(*map(int, timestamp_value["time"].split(":")))
        payload["timestamp"] = datetime.combine(date_obj, time_obj)

        return HistoryRecord(**payload).model_dump()


if __name__ == "__main__":
    example = {
        "timestamp": datetime.now(),
        "city": "Moscow",
        "temperature": 25,
        "weather_type": WeatherTypeOpenweathermap.CLOUDS,
        "sunrise": "07:30",
        "sunset": "18:00",
    }

    hr = HistoryRecord(**example)

    data_str = str(hr)
    data_dict = HistoryRecord.str2dict(data_str)

    pprint(data_str)
    pprint(data_dict)
