import os
import sys
from datetime import datetime, time

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from sqlalchemy import UniqueConstraint  # noqa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # noqa

from database.db import Base  # noqa
from models.domains import WeatherTypeOpenweathermap  # noqa


class WeatherORMModel(Base):
    __tablename__ = "weather_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime]
    city: Mapped[str]
    temperature: Mapped[int]
    weather_type: Mapped[WeatherTypeOpenweathermap]
    sunrise: Mapped[time]
    sunset: Mapped[time]

    # UniqueConstraint на комбинацию столбцов timestamp и city
    __table_args__ = (UniqueConstraint("timestamp", "city", name="uq_timestamp_city"),)


class TextfileEntity(str):
    """
    Custom class representing a formatted text entity.

    This class is a subclass of the built-in str class and is intended to represent
    a specific format of text, such as the result of formatting weather data.

    The expected format of the string is as follows:
    Date: {date}\n
    Time: {time} UTC\n
    City: {city}\n
    Temperature: {temperature} °C\n
    Weather type: {weather_type}\n
    Sunrise: {sunrise} UTC\n
    Sunset: {sunset} UTC

    Usage:
    text_entity = TextfileEntity("Your formatted text here")

    Note: You can customize this class by adding your own methods if needed.
    """

    pass


class JsonEntity(dict):
    """
    Custom class representing a JSON entity.

    This class is a subclass of the built-in dict class and is intended to represent
    a JSON-like structure with additional functionality.

    The expected format of time and date fields in ISO format:
    - 'timestamp': {timestamp} (ISO format)
    - 'sunrise': {sunrise} (ISO format)
    - 'sunset': {sunset} (ISO format)

    Usage:
    json_entity = JsonEntity({
        'timestamp': '2023-01-01T12:30:45',
        'sunrise': '06:00:00',
        'sunset': '18:00:00',
        'other_field': 'other_value'
    })

    Note: You can customize this class by adding your own methods if needed.
    """

    pass


if __name__ == "__main__":
    formatted_string = (
        "Date: 2023-12-01\n"
        "Time: 12:30 UTC\n"
        "City: ExampleCity\n"
        "Temperature: 25 °C\n"
        "Weather type: Sunny\n"
        "Sunrise: 06:00 UTC\n"
        "Sunset: 18:00 UTC"
    )
    entity = TextfileEntity(formatted_string)

    print(entity)
