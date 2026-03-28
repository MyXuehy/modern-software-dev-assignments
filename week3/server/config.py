from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    weather_base_url: str
    geocoding_base_url: str
    weather_api_key: str | None
    request_timeout_seconds: float
    max_retries: int
    retry_backoff_seconds: float
    use_mock_api: bool


    @staticmethod
    def from_env() -> "Settings":
        timeout_raw = os.getenv("REQUEST_TIMEOUT_SECONDS", "8")
        max_retries_raw = os.getenv("MAX_RETRIES", "2")
        retry_backoff_raw = os.getenv("RETRY_BACKOFF_SECONDS", "0.4")
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be a number") from exc

        try:
            max_retries = int(max_retries_raw)
        except ValueError as exc:
            raise ValueError("MAX_RETRIES must be an integer") from exc

        try:
            retry_backoff = float(retry_backoff_raw)
        except ValueError as exc:
            raise ValueError("RETRY_BACKOFF_SECONDS must be a number") from exc

        if timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT_SECONDS must be > 0")

        if max_retries < 0:
            raise ValueError("MAX_RETRIES must be >= 0")

        if retry_backoff <= 0:
            raise ValueError("RETRY_BACKOFF_SECONDS must be > 0")

        return Settings(
            weather_base_url=os.getenv("WEATHER_BASE_URL", "https://api.open-meteo.com/v1"),
            geocoding_base_url=os.getenv(
                "GEOCODING_BASE_URL", "https://geocoding-api.open-meteo.com/v1"
            ),
            weather_api_key=os.getenv("WEATHER_API_KEY"),
            request_timeout_seconds=timeout,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff,
            use_mock_api=os.getenv("USE_MOCK_API", "true").lower() == "true",
        )

