import os
import sys
from datetime import date, datetime, time

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from mappers.abstractions import AbstractDomainEntityMapper, AbstractDTOMapper  # noqa
from models.domains import Celsius, WeatherDomain, WeatherTypeOpenweathermap  # noqa
from models.dto import JsonOpenweathermapResponseDTO  # noqa
from models.entities import JsonEntity, TextfileEntity, WeatherORMModel  # noqa


class OpenweathermapWeatherMapper(
    AbstractDTOMapper[JsonOpenweathermapResponseDTO, WeatherDomain]
):
    def to_target(self, source_obj: JsonOpenweathermapResponseDTO) -> WeatherDomain:
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

        return WeatherDomain(
            timestamp=source_obj["timestamp"].replace(microsecond=0),
            city=source_obj["name"],
            temperature=Celsius(source_obj["main"]["temp"] - 273),
            weather_type=WeatherTypeOpenweathermap(
                translation[source_obj["weather"][0]["main"].upper()]
            ),
            sunrise=datetime.fromtimestamp(source_obj["sys"]["sunrise"]).time(),
            sunset=datetime.fromtimestamp(source_obj["sys"]["sunset"]).time(),
        )


class WeatherDatabaseMapper(AbstractDomainEntityMapper[WeatherDomain, WeatherORMModel]):
    def to_entity(self, domain_obj: WeatherDomain) -> WeatherORMModel:
        return WeatherORMModel(**domain_obj.model_dump())

    def to_domain(self, entity_obj: WeatherORMModel) -> WeatherDomain:
        payload = {
            column: getattr(entity_obj, column)
            for column in entity_obj.__table__.c.keys()
        }
        return WeatherDomain(**payload)


class TextfileMapper(AbstractDomainEntityMapper[WeatherDomain, TextfileEntity]):
    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M"

    def to_entity(self, domain_obj: WeatherDomain) -> TextfileEntity:
        domain_dict = domain_obj.model_dump()
        formatted_string = (
            f"Date: {domain_dict['timestamp'].date().strftime(self.DATE_FORMAT)}\n"
            f"Time: {domain_dict['timestamp'].time().strftime(self.TIME_FORMAT)} UTC\n"
            f"City: {domain_dict['city']}\n"
            f"Temperature: {domain_dict['temperature']} °C\n"
            f"Weather type: {domain_dict['weather_type'].value}\n"
            f"Sunrise: {domain_dict['sunrise'].strftime(self.TIME_FORMAT)} UTC\n"
            f"Sunset: {domain_dict['sunset'].strftime(self.TIME_FORMAT)} UTC"
        )
        return TextfileEntity(formatted_string)

    def to_domain(self, entity_obj: TextfileEntity) -> WeatherDomain:
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

        return WeatherDomain(**result)


class JsonMapper(AbstractDomainEntityMapper[WeatherDomain, JsonEntity]):
    def to_entity(self, domain_obj: WeatherDomain) -> JsonEntity:
        payload = domain_obj.model_dump()

        formatted_time = payload["timestamp"].isoformat()
        formatted_sunrise = payload["sunrise"].isoformat()
        formatted_sunset = payload["sunset"].isoformat()
        payload["timestamp"] = formatted_time
        payload["sunrise"] = formatted_sunrise
        payload["sunset"] = formatted_sunset

        return JsonEntity(payload)

    def to_domain(self, entity_obj: JsonEntity) -> WeatherDomain:
        return WeatherDomain(**entity_obj)
