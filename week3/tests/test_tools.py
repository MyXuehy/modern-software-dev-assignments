from week3.server.client import WeatherApiClient
from week3.server.config import Settings
from week3.server.tools import ToolRegistry


def test_tool_registry_current_weather_mock() -> None:
    settings = Settings(
        weather_base_url="https://api.open-meteo.com/v1",
        geocoding_base_url="https://geocoding-api.open-meteo.com/v1",
        weather_api_key=None,
        request_timeout_seconds=8.0,
        max_retries=2,
        retry_backoff_seconds=0.2,
        use_mock_api=True,
    )
    registry = ToolRegistry(client=WeatherApiClient(settings=settings))

    result = registry.call("get_current_weather", {"city": "Shanghai"})

    assert result["tool"] == "get_current_weather"
    assert result["result"]["city"] == "Shanghai"


def test_tool_registry_forecast_mock() -> None:
    settings = Settings(
        weather_base_url="https://api.open-meteo.com/v1",
        geocoding_base_url="https://geocoding-api.open-meteo.com/v1",
        weather_api_key=None,
        request_timeout_seconds=8.0,
        max_retries=2,
        retry_backoff_seconds=0.2,
        use_mock_api=True,
    )
    registry = ToolRegistry(client=WeatherApiClient(settings=settings))

    result = registry.call("get_forecast", {"city": "Shanghai", "days": 2})

    assert result["tool"] == "get_forecast"
    assert len(result["result"]["forecast"]) == 2


