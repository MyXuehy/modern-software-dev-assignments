from week3.server.client import WeatherApiClient
from week3.server.config import Settings
from week3.server.tools import ToolRegistry


def test_tool_registry_current_weather_mock() -> None:
    settings = Settings(
        weather_base_url="https://api.open-meteo.com/v1",
        weather_api_key=None,
        request_timeout_seconds=8.0,
        use_mock_api=True,
    )
    registry = ToolRegistry(client=WeatherApiClient(settings=settings))

    result = registry.call("get_current_weather", {"city": "Shanghai"})

    assert result["tool"] == "get_current_weather"
    assert result["result"]["city"] == "Shanghai"

