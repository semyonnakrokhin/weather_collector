import os
import sys
from datetime import datetime, time

parent_directory = os.path.join(os.getcwd(), "..")
sys.path.append(parent_directory)

from sqlalchemy import UniqueConstraint  # noqa
from sqlalchemy.orm import Mapped, mapped_column  # noqa

from database.db import Base  # noqa
from schemas import WeatherTypeOpenweathermap  # noqa


class WeatherModel(Base):
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


if __name__ == "__main__":
    c = 1
