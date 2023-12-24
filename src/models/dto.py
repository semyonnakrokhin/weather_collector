from datetime import datetime
from typing import TypedDict


class JsonOpenweathermapResponseDTO(TypedDict):
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
