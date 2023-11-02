import json
from abc import ABC
from datetime import date, datetime, time
from typing import Generic, Type, TypeVar

from models.models import WeatherModel
from schemas import (
    Celsius,
    JsonOpenweathermapResponse,
    Weather,
    WeatherTypeOpenweathermap,
)

#########################################################
##############      Abstract classes      ############### # noqa
#########################################################


D = TypeVar("D")
E = TypeVar("E")


class AbstractRepositoryMapper(ABC, Generic[D, E]):
    domain_model_type: Type[D]
    entity_type: Type[E]

    @classmethod
    def to_domain(cls, entity_obj: E) -> D:
        pass

    @classmethod
    def to_entity(cls, domain_obj: D) -> E:
        pass


S = TypeVar("S")
T = TypeVar("T")


class AbstractControllerMapper(ABC, Generic[S, T]):
    source_type: Type[S]
    target_type: Type[T]

    @classmethod
    def to_target(cls, source_obj: S) -> T:
        pass

    @classmethod
    def to_source(cls, target_obj: T) -> S:
        pass


#############################################################
##############          Realisations          ############### # noqa
#############################################################


class WeatherMapper(AbstractControllerMapper[JsonOpenweathermapResponse, Weather]):
    """
    source_type: JsonOpenweathermapResponse
    target_type: Weather
    """

    @classmethod
    def to_target(cls, source_obj: JsonOpenweathermapResponse) -> Weather:
        translation = {
            "THUNDERSTORM": "Гроза",
            "DRIZZLE": "Изморось",
            "RAIN": "Дождь",
            "SNOW": "Снег",
            "MIST": "Туманная дымка",
            "SMOKE": "Копоть",
            "HAZE": "Мгла",
            "DUST": "Пыль",
            "FOG": "Туман",
            "SAND": "Песок",
            "ASH": "Пепел",
            "SQUALL": "Шквал",
            "TORNADO": "Торнадо",
            "CLEAR": "Ясно",
            "CLOUDS": "Облачно",
        }

        return Weather(
            timestamp=source_obj["timestamp"],
            city=source_obj["name"],
            temperature=Celsius(source_obj["main"]["temp"] - 273),
            weather_type=WeatherTypeOpenweathermap(
                translation[source_obj["weather"][0]["main"].upper()]
            ),
            sunrise=datetime.fromtimestamp(source_obj["sys"]["sunrise"]).time(),
            sunset=datetime.fromtimestamp(source_obj["sys"]["sunset"]).time(),
        )


class DBMapper(AbstractRepositoryMapper[dict, WeatherModel]):
    """
    domain_model_type: dict (Weather)
    entity_type: WeatherModel
    """

    @classmethod
    def to_domain(cls, entity_obj: WeatherModel) -> dict:
        return {
            column: getattr(entity_obj, column)
            for column in entity_obj.__table__.c.keys()
        }

    @classmethod
    def to_entity(cls, domain_obj: dict) -> WeatherModel:
        pass


class FileMapper(AbstractRepositoryMapper[dict, str]):
    """
    domain_model_type: dict (Weather)
    entity_type: str
    """

    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M"

    @classmethod
    def to_domain(cls, entity_obj: str) -> dict:
        lines = entity_obj.strip().split("\n")

        timestamp_value = {}
        result = {}
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

            result[_key.lower()] = __value

        date_obj = date(*map(int, timestamp_value["date"].split(".")[::-1]))
        time_obj = time(*map(int, timestamp_value["time"].split(":")))
        result["timestamp"] = datetime.combine(date_obj, time_obj)

        return result

    @classmethod
    def to_entity(cls, domain_obj: dict) -> str:
        return (
            f"Date: {domain_obj['timestamp'].date().strftime(cls.DATE_FORMAT)}\n"
            f"Time: {domain_obj['timestamp'].time().strftime(cls.TIME_FORMAT)} UTC\n"
            f"City: {domain_obj['city']}\n"
            f"Temperature: {domain_obj['temperature']} °C\n"
            f"Weather type: {domain_obj['weather_type'].value}\n"
            f"Sunrise: {domain_obj['sunrise'].strftime(cls.TIME_FORMAT)} UTC\n"
            f"Sunset: {domain_obj['sunset'].strftime(cls.TIME_FORMAT)} UTC\n"
            "\n"
        )


class JSONMapper(AbstractRepositoryMapper[dict, str]):
    """
    domain_model_type: dict (Weather)
    entity_type: str (json)
    """

    @classmethod
    def to_domain(cls, entity_obj: str) -> dict:
        data_dict = json.loads(entity_obj)
        return data_dict

    @classmethod
    def to_entity(cls, domain_obj: dict) -> str:
        formatted_time = domain_obj["timestamp"].replace(microsecond=0).isoformat()
        formatted_sunrise = domain_obj["sunrise"].isoformat()
        formatted_sunset = domain_obj["sunset"].isoformat()
        domain_obj["timestamp"] = formatted_time
        domain_obj["sunrise"] = formatted_sunrise
        domain_obj["sunset"] = formatted_sunset
        json_str = json.dumps(domain_obj, indent=2, ensure_ascii=False)
        return json_str
