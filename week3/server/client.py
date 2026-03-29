from __future__ import annotations

import time
from typing import Any, Callable

import httpx

from .config import Settings
from .errors import ExternalApiError, RateLimitError, TimeoutAppError

WEATHER_CODE_TO_TEXT = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherApiClient:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self._settings = settings
        self._transport = transport
        self._sleep = sleep_fn or time.sleep

    def get_current_weather(self, city: str) -> dict:
        if self._settings.use_mock_api:
            return {
                "city": city,
                "temperature_c": 22.3,
                "condition": "Partly cloudy",
                "source": "mock",
            }

        location = self._resolve_location(city)
        payload = self._request_json(
            base_url=self._settings.weather_base_url,
            path="/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
        )

        current = payload.get("current") or {}
        weather_code = current.get("weather_code")
        return {
            "city": location["resolved_name"],
            "query_city": city,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "weather_code": weather_code,
            "condition": self._weather_text(weather_code),
            "source": "open-meteo",
        }

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

        location = self._resolve_location(city)
        payload = self._request_json(
            base_url=self._settings.weather_base_url,
            path="/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "forecast_days": days,
                "timezone": "auto",
            },
        )

        daily = payload.get("daily") or {}
        times = daily.get("time") or []
        highs = daily.get("temperature_2m_max") or []
        lows = daily.get("temperature_2m_min") or []
        codes = daily.get("weather_code") or []

        if not times:
            raise ExternalApiError("Forecast data is empty for this location")

        forecast: list[dict[str, Any]] = []
        for index, date in enumerate(times):
            weather_code = codes[index] if index < len(codes) else None
            forecast.append(
                {
                    "date": date,
                    "high_c": highs[index] if index < len(highs) else None,
                    "low_c": lows[index] if index < len(lows) else None,
                    "weather_code": weather_code,
                    "condition": self._weather_text(weather_code),
                }
            )

        return {
            "city": location["resolved_name"],
            "query_city": city,
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "days": days,
            "forecast": forecast,
            "source": "open-meteo",
        }

    def _resolve_location(self, city: str) -> dict[str, Any]:
        payload = self._request_json(
            base_url=self._settings.geocoding_base_url,
            path="/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        results = payload.get("results") or []
        if not results:
            raise ExternalApiError(f"City not found: {city}")

        location = results[0]
        return {
            "resolved_name": self._format_location_name(location),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
        }

    def _request_json(self, base_url: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None

        for attempt in range(self._settings.max_retries + 1):
            try:
                with httpx.Client(
                    base_url=base_url,
                    timeout=self._settings.request_timeout_seconds,
                    transport=self._transport,
                ) as client:
                    response = client.get(path, params=params)
            except httpx.TimeoutException as exc:
                last_error = TimeoutAppError("Weather API request timed out")
                if attempt < self._settings.max_retries:
                    self._backoff(attempt)
                    continue
                raise last_error from exc
            except httpx.HTTPError as exc:
                raise ExternalApiError(f"Weather API HTTP error: {exc}") from exc

            if response.status_code == 429:
                last_error = RateLimitError("Weather API rate limit exceeded")
                if attempt < self._settings.max_retries:
                    self._backoff(attempt)
                    continue
                raise last_error

            if response.status_code >= 500:
                last_error = ExternalApiError(f"Weather API server error ({response.status_code})")
                if attempt < self._settings.max_retries:
                    self._backoff(attempt)
                    continue
                raise last_error

            if response.status_code >= 400:
                raise ExternalApiError(f"Weather API request failed ({response.status_code})")

            try:
                payload = response.json()
            except ValueError as exc:
                raise ExternalApiError("Weather API returned invalid JSON") from exc

            if not isinstance(payload, dict):
                raise ExternalApiError("Weather API payload format is invalid")

            return payload

        if last_error:
            raise last_error
        raise ExternalApiError("Weather API request failed unexpectedly")

    def _backoff(self, attempt: int) -> None:
        # Why: bounded exponential backoff reduces burst retries during transient
        # 429/5xx responses and helps avoid amplifying provider-side overload.
        delay = self._settings.retry_backoff_seconds * (2**attempt)
        self._sleep(delay)

    def _format_location_name(self, location: dict[str, Any]) -> str:
        parts = [location.get("name"), location.get("admin1"), location.get("country")]
        return ", ".join([str(part) for part in parts if part])

    def _weather_text(self, weather_code: Any) -> str:
        if weather_code is None:
            return "Unknown"
        try:
            normalized_code = int(weather_code)
        except (TypeError, ValueError):
            return "Unknown"
        return WEATHER_CODE_TO_TEXT.get(normalized_code, "Unknown")
