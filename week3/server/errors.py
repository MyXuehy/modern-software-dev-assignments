from __future__ import annotations

from dataclasses import dataclass


class AppError(Exception):
    """Base application error for predictable user-facing responses."""

    code = "internal_error"


class ValidationAppError(AppError):
    code = "validation_error"


class ToolNotFoundError(AppError):
    code = "tool_not_found"


class ExternalApiError(AppError):
    code = "external_api_error"


class RateLimitError(ExternalApiError):
    code = "rate_limited"


class TimeoutAppError(ExternalApiError):
    code = "upstream_timeout"


@dataclass
class ErrorResponse:
    ok: bool
    error: dict[str, str]


def build_error_response(exc: Exception) -> ErrorResponse:
    if isinstance(exc, AppError):
        return ErrorResponse(ok=False, error={"code": exc.code, "message": str(exc)})
    return ErrorResponse(ok=False, error={"code": "internal_error", "message": "Unexpected error"})
