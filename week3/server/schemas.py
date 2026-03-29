from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CurrentWeatherArgs(BaseModel):
    city: str = Field(min_length=1, max_length=100)

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("city cannot be blank")
        return value


class ForecastArgs(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    days: int = Field(default=3, ge=1, le=7)

    @field_validator("city")
    @classmethod
    def city_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("city cannot be blank")
        return value


class ToolCallRequest(BaseModel):
    tool: str = Field(min_length=1)
    arguments: dict


class ToolCallSuccess(BaseModel):
    ok: bool = True
    data: dict
