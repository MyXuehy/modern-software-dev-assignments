import pytest
from pydantic import ValidationError

from week3.server.schemas import CurrentWeatherArgs, ForecastArgs


def test_current_weather_args_city_trimmed() -> None:
    parsed = CurrentWeatherArgs.model_validate({"city": "  Shanghai  "})
    assert parsed.city == "Shanghai"


def test_forecast_days_range() -> None:
    with pytest.raises(ValidationError):
        ForecastArgs.model_validate({"city": "Shanghai", "days": 8})
