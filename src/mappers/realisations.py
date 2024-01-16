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
    """OpenweathermapWeatherMapper implements the AbstractDTOMapper interface
    for transforming OpenWeatherMap weather data from DTO to the domain
    model."""

    def to_target(self, source_obj: JsonOpenweathermapResponseDTO) -> WeatherDomain:
        """Maps data from a JsonOpenweathermapResponseDTO to a WeatherDomain
        object.

        Args:
            source_obj (JsonOpenweathermapResponseDTO): The source DTO
            representing OpenWeatherMap weather data.

        Returns:
            WeatherDomain: The target domain model object representing weather
            information.
        """

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
    """WeatherDatabaseMapper implements the AbstractDomainEntityMapper
    interface for transforming weather data between the domain model and the
    database entity."""

    def to_entity(self, domain_obj: WeatherDomain) -> WeatherORMModel:
        """Maps data from a WeatherDomain object to a WeatherORMModel entity.

        Args:
            domain_obj (WeatherDomain): The source domain model representing
            weather data.

        Returns:
            WeatherORMModel: The target entity object representing
            weather data in the database.
        """

        return WeatherORMModel(**domain_obj.model_dump())

    def to_domain(self, entity_obj: WeatherORMModel) -> WeatherDomain:
        """Maps data from a WeatherORMModel entity to a WeatherDomain object.

        Args:
            entity_obj (WeatherORMModel): The source entity object representing
            weather data in the database.

        Returns:
            WeatherDomain: The target domain model object representing weather data.
        """

        payload = {
            column: getattr(entity_obj, column)
            for column in entity_obj.__table__.c.keys()
        }
        return WeatherDomain(**payload)


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
        """Maps data from a WeatherDomain object to a TextfileEntity.

        Args:
            domain_obj (WeatherDomain): The source domain model
            representing weather data.

        Returns:
            TextfileEntity: The target entity object
            representing weather data in a text file.
        """

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
        """Maps data from a TextfileEntity to a WeatherDomain object.

        Args:
            entity_obj (TextfileEntity): The source entity object
            representing weather data in a text file.

        Returns:
            WeatherDomain: The target domain model object representing weather data.
        """

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
    """JsonMapper implements the AbstractDomainEntityMapper interface for
    transforming weather data between the domain model and a JSON file
    entity."""

    def to_entity(self, domain_obj: WeatherDomain) -> JsonEntity:
        """Maps data from a WeatherDomain object to a JsonEntity.

        Args:
            domain_obj (WeatherDomain): The source domain model
            representing weather data.

        Returns:
            JsonEntity: The target entity object
            representing weather data in JSON format.
        """

        payload = domain_obj.model_dump()

        formatted_time = payload["timestamp"].isoformat()
        formatted_sunrise = payload["sunrise"].isoformat()
        formatted_sunset = payload["sunset"].isoformat()
        payload["timestamp"] = formatted_time
        payload["sunrise"] = formatted_sunrise
        payload["sunset"] = formatted_sunset

        return JsonEntity(payload)

    def to_domain(self, entity_obj: JsonEntity) -> WeatherDomain:
        """Maps data from a JsonEntity to a WeatherDomain object.

        Args:
            entity_obj (JsonEntity): The source entity object
            representing weather data in JSON format.

        Returns:
            WeatherDomain: The target domain model object representing weather data.
        """

        return WeatherDomain(**entity_obj)
