from week3.server.client import WeatherApiClient
from week3.server.config import Settings
from week3.server.mcp_stdio import handle_message
from week3.server.tools import ToolRegistry


def _registry() -> ToolRegistry:
    settings = Settings(
        weather_base_url="https://api.open-meteo.com/v1",
        geocoding_base_url="https://geocoding-api.open-meteo.com/v1",
        weather_api_key=None,
        request_timeout_seconds=8.0,
        max_retries=1,
        retry_backoff_seconds=0.1,
        use_mock_api=True,
    )
    return ToolRegistry(client=WeatherApiClient(settings=settings))


def test_initialize_response_contains_tools_capability() -> None:
    response = handle_message(
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        _registry(),
    )

    assert response is not None
    assert response["result"]["capabilities"]["tools"] == {}


def test_tools_list_contains_two_tools() -> None:
    response = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, _registry())

    assert response is not None
    assert len(response["result"]["tools"]) == 2


def test_tools_call_success() -> None:
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_current_weather", "arguments": {"city": "Shanghai"}},
        },
        _registry(),
    )

    assert response is not None
    assert response["result"]["isError"] is False
    assert response["result"]["structuredContent"]["city"] == "Shanghai"


def test_tools_call_validation_error() -> None:
    response = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "get_forecast", "arguments": {"city": "Shanghai", "days": 99}},
        },
        _registry(),
    )

    assert response is not None
    assert response["error"]["code"] == -32602

