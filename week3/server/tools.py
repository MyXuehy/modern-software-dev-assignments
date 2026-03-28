from __future__ import annotations

from pydantic import ValidationError

from .client import WeatherApiClient
from .errors import ToolNotFoundError, ValidationAppError
from .schemas import CurrentWeatherArgs, ForecastArgs


class ToolRegistry:
    def __init__(self, client: WeatherApiClient) -> None:
        self._client = client

    def call(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "get_current_weather":
            return self._handle_current_weather(arguments)

        if tool_name == "get_forecast":
            return self._handle_forecast(arguments)

        raise ToolNotFoundError(f"Unsupported tool: {tool_name}")

    def _handle_current_weather(self, arguments: dict) -> dict:
        try:
            parsed = CurrentWeatherArgs.model_validate(arguments)
        except ValidationError as exc:
            raise ValidationAppError(str(exc)) from exc

        data = self._client.get_current_weather(city=parsed.city)
        return {"tool": "get_current_weather", "result": data}

    def _handle_forecast(self, arguments: dict) -> dict:
        try:
            parsed = ForecastArgs.model_validate(arguments)
        except ValidationError as exc:
            raise ValidationAppError(str(exc)) from exc

        data = self._client.get_forecast(city=parsed.city, days=parsed.days)
        return {"tool": "get_forecast", "result": data}

