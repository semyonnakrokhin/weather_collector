import logging
import os
import sys
from datetime import date, datetime, time
from typing import NoReturn, Union

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from exceptions import MappingError  # noqa
from mappers.abstractions import AbstractDomainEntityMapper, AbstractDTOMapper  # noqa
from models.domains import Celsius, WeatherDomain, WeatherTypeOpenweathermap  # noqa
from models.dto import JsonOpenweathermapResponseDTO  # noqa
from models.entities import JsonEntity, TextfileEntity, WeatherORMModel  # noqa

logger = logging.getLogger("app.mappers")


class OpenweathermapWeatherMapper(
    AbstractDTOMapper[JsonOpenweathermapResponseDTO, WeatherDomain]
):
    """OpenweathermapWeatherMapper implements the AbstractDTOMapper interface
    for transforming OpenWeatherMap weather data from DTO to the domain
    model."""

    def to_target(
        self, source_obj: JsonOpenweathermapResponseDTO
    ) -> Union[WeatherDomain, NoReturn]:
        """Maps data from a JsonOpenweathermapResponseDTO to a WeatherDomain
        object."""

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

        try:
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
        except KeyError as e:
            error_message = (
                f"Error mapping weather data: Missing key {str(e)} "
                f"in source object {type(source_obj)}."
            )
            logger.error(error_message)
            raise MappingError(error_message)
        except Exception as e:
            error_message = (
                f"Unexpected error occurred during weather mapping: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)


class WeatherDatabaseMapper(AbstractDomainEntityMapper[WeatherDomain, WeatherORMModel]):
    """WeatherDatabaseMapper implements the AbstractDomainEntityMapper
    interface for transforming weather data between the domain model and the
    database entity."""

    def to_entity(self, domain_obj: WeatherDomain) -> Union[WeatherORMModel, NoReturn]:
        """Maps data from a WeatherDomain object to a WeatherORMModel entity."""

        try:
            return WeatherORMModel(**domain_obj.model_dump())
        except Exception as e:
            error_message = f"Error mapping WeatherDomain to WeatherORMModel: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: WeatherORMModel) -> Union[WeatherDomain, NoReturn]:
        """Maps data from a WeatherORMModel entity to a WeatherDomain object."""

        try:
            payload = {
                column: getattr(entity_obj, column)
                for column in entity_obj.__table__.c.keys()
            }
            return WeatherDomain(**payload)
        except Exception as e:
            error_message = f"Error mapping WeatherORMModel to WeatherDomain: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)


class TextfileMapper(AbstractDomainEntityMapper[WeatherDomain, TextfileEntity]):
    """TextfileMapper implements the AbstractDomainEntityMapper interface for
    transforming weather data between the domain model and a text file entity.

    Attributes:
        DATE_FORMAT (str): Date format for formatting timestamps in the text file.
        TIME_FORMAT (str): Time format for formatting timestamps in the text file.
    """

    DATE_FORMAT = "%d.%m.%Y"
    TIME_FORMAT = "%H:%M"

    def to_entity(self, domain_obj: WeatherDomain) -> TextfileEntity:
        """Maps data from a WeatherDomain object to a TextfileEntity."""

        try:
            domain_dict = domain_obj.model_dump()
            formatted_string = (
                f"Date: {domain_dict['timestamp'].date().strftime(self.DATE_FORMAT)}\n"
                f"Time: {domain_dict['timestamp'].time().strftime(self.TIME_FORMAT)}"
                f" UTC\n"
                f"City: {domain_dict['city']}\n"
                f"Temperature: {domain_dict['temperature']} °C\n"
                f"Weather type: {domain_dict['weather_type'].value}\n"
                f"Sunrise: {domain_dict['sunrise'].strftime(self.TIME_FORMAT)} UTC\n"
                f"Sunset: {domain_dict['sunset'].strftime(self.TIME_FORMAT)} UTC"
            )
            return TextfileEntity(formatted_string)
        except Exception as e:
            error_message = f"Error mapping WeatherDomain to TextfileEntity: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: TextfileEntity) -> Union[WeatherDomain, NoReturn]:
        """Maps data from a TextfileEntity to a WeatherDomain object."""

        try:
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
        except (KeyError, ValueError) as e:
            error_message = f"Error extracting date and time data: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)
        except Exception as e:
            error_message = (
                f"Unexpected error occurred during weather mapping: {str(e)}"
            )
            logger.error(error_message)
            raise MappingError(error_message)


class JsonMapper(AbstractDomainEntityMapper[WeatherDomain, JsonEntity]):
    """JsonMapper implements the AbstractDomainEntityMapper interface for
    transforming weather data between the domain model and a JSON file
    entity."""

    def to_entity(self, domain_obj: WeatherDomain) -> JsonEntity:
        """Maps data from a WeatherDomain object to a JsonEntity."""

        try:
            payload = domain_obj.model_dump()

            formatted_time = payload["timestamp"].isoformat()
            formatted_sunrise = payload["sunrise"].isoformat()
            formatted_sunset = payload["sunset"].isoformat()
            payload["timestamp"] = formatted_time
            payload["sunrise"] = formatted_sunrise
            payload["sunset"] = formatted_sunset

            return JsonEntity(payload)
        except Exception as e:
            error_message = f"Error mapping WeatherDomain to JsonEntity: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)

    def to_domain(self, entity_obj: JsonEntity) -> WeatherDomain:
        """Maps data from a JsonEntity to a WeatherDomain object."""

        try:
            return WeatherDomain(**entity_obj)
        except Exception as e:
            error_message = f"Error mapping JsonEntity to WeatherDomain: {str(e)}"
            logger.error(error_message)
            raise MappingError(error_message)
