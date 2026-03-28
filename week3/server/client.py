from __future__ import annotations

from .config import Settings
from .errors import ExternalApiError


class WeatherApiClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_current_weather(self, city: str) -> dict:
        if self._settings.use_mock_api:
            return {
                "city": city,
                "temperature_c": 22.3,
                "condition": "Partly cloudy",
                "source": "mock",
            }

        # Why: fail fast when real API mode is enabled but integration is not done,
        # to avoid returning misleading fake data in production evaluation.
        raise ExternalApiError("Real weather API integration is not implemented yet")

    def get_forecast(self, city: str, days: int) -> dict:
        if self._settings.use_mock_api:
            forecast = []
            for index in range(days):
                forecast.append(
                    {
                        "day": index + 1,
                        "high_c": 25 + index,
                        "low_c": 16 + index,
                        "condition": "Sunny" if index % 2 == 0 else "Cloudy",
                    }
                )
            return {"city": city, "days": days, "forecast": forecast, "source": "mock"}

        raise ExternalApiError("Real weather API integration is not implemented yet")

