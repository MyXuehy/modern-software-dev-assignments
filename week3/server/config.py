from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    weather_base_url: str
    weather_api_key: str | None
    request_timeout_seconds: float
    use_mock_api: bool


    @staticmethod
    def from_env() -> "Settings":
        timeout_raw = os.getenv("REQUEST_TIMEOUT_SECONDS", "8")
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be a number") from exc

        if timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be > 0")

        return Settings(
            weather_base_url=os.getenv("WEATHER_BASE_URL", "https://api.open-meteo.com/v1"),
            weather_api_key=os.getenv("WEATHER_API_KEY"),
            request_timeout_seconds=timeout,
            use_mock_api=os.getenv("USE_MOCK_API", "true").lower() == "true",
        )

