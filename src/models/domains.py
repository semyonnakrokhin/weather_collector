from datetime import datetime, time
from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel


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


class WeatherDomain(BaseModel):
    timestamp: datetime
    city: str
    temperature: Celsius
    weather_type: WeatherTypeOpenweathermap
    sunrise: time
    sunset: time
