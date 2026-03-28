import json

import httpx
import pytest

from week3.server.client import WeatherApiClient
from week3.server.config import Settings
from week3.server.errors import ExternalApiError, RateLimitError


def _real_mode_settings(max_retries: int = 0) -> Settings:
    return Settings(
        weather_base_url="https://api.open-meteo.com/v1",
        geocoding_base_url="https://geocoding-api.open-meteo.com/v1",
        weather_api_key=None,
        request_timeout_seconds=5.0,
        max_retries=max_retries,
        retry_backoff_seconds=0.01,
        use_mock_api=False,
    )


def test_get_current_weather_real_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Shanghai",
                            "admin1": "Shanghai",
                            "country": "China",
                            "latitude": 31.23,
                            "longitude": 121.47,
                        }
                    ]
                },
            )

        if request.url.host == "api.open-meteo.com":
            return httpx.Response(
                200,
                json={
                    "current": {
                        "temperature_2m": 23.1,
                        "apparent_temperature": 22.5,
                        "weather_code": 2,
                        "wind_speed_10m": 11.3,
                    }
                },
            )

        return httpx.Response(404, json={"error": "unexpected host"})

    client = WeatherApiClient(
        settings=_real_mode_settings(),
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _: None,
    )

    result = client.get_current_weather("Shanghai")

    assert result["source"] == "open-meteo"
    assert result["temperature_c"] == 23.1
    assert result["condition"] == "Partly cloudy"


def test_get_forecast_city_not_found() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    client = WeatherApiClient(
        settings=_real_mode_settings(),
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _: None,
    )

    with pytest.raises(ExternalApiError, match="City not found"):
        client.get_forecast("Unknown-City", days=2)


def test_get_current_weather_rate_limited() -> None:
    counter = {"calls": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        counter["calls"] += 1
        if request.url.host == "geocoding-api.open-meteo.com":
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Shanghai",
                            "country": "China",
                            "latitude": 31.23,
                            "longitude": 121.47,
                        }
                    ]
                },
            )

        return httpx.Response(429, content=json.dumps({"reason": "rate limit"}))

    client = WeatherApiClient(
        settings=_real_mode_settings(max_retries=1),
        transport=httpx.MockTransport(handler),
        sleep_fn=lambda _: None,
    )

    with pytest.raises(RateLimitError):
        client.get_current_weather("Shanghai")

    assert counter["calls"] == 3

