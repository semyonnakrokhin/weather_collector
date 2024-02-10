import datetime

city_payload_1 = {
    "coord": {"lon": 117.1767, "lat": 39.1422},
    "weather": [
        {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}
    ],
    "base": "stations",
    "main": {
        "temp": 270.12,
        "feels_like": 265.14,
        "temp_min": 270.12,
        "temp_max": 270.12,
        "pressure": 1032,
        "humidity": 46,
    },
    "visibility": 10000,
    "wind": {"speed": 4, "deg": 320},
    "clouds": {"all": 0},
    "dt": 1707253890,
    "sys": {
        "type": 1,
        "id": 9619,
        "country": "CN",
        "sunrise": 1707261198,
        "sunset": 1707298648,
    },
    "timezone": 28800,
    "id": 1792947,
    "name": "City1",
    "cod": 200,
    "timestamp": datetime.datetime(2024, 2, 6, 21, 11, 30, 677037),
}

city_payload_2 = {
    "coord": {"lon": 117.1767, "lat": 39.1422},
    "weather": [
        {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04n"}
    ],
    "base": "stations",
    "main": {
        "temp": 268.42,
        "feels_like": 263.37,
        "temp_min": 268.42,
        "temp_max": 268.42,
        "pressure": 1031,
        "humidity": 49,
    },
    "visibility": 10000,
    "wind": {"speed": 3, "deg": 20},
    "clouds": {"all": 100},
    "dt": 1707253890,
    "sys": {
        "type": 1,
        "id": 9619,
        "country": "CN",
        "sunrise": 1707261198,
        "sunset": 1707298648,
    },
    "timezone": 28800,
    "id": 1792947,
    "name": "City2",
    "cod": 200,
    "timestamp": datetime.datetime(2024, 2, 6, 21, 11, 30, 677037),
}

response_data = {
    "coord": {"lon": 117.1767, "lat": 39.1422},
    "weather": [
        {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04n"}
    ],
    "base": "stations",
    "main": {
        "temp": 268.42,
        "feels_like": 263.37,
        "temp_min": 268.42,
        "temp_max": 268.42,
        "pressure": 1031,
        "humidity": 49,
    },
    "visibility": 10000,
    "wind": {"speed": 3, "deg": 20},
    "clouds": {"all": 100},
    "dt": 1707253890,
    "sys": {
        "type": 1,
        "id": 9619,
        "country": "CN",
        "sunrise": 1707261198,
        "sunset": 1707298648,
    },
    "timezone": 28800,
    "id": 1792947,
    "name": "City1",
    "cod": 200,
}
