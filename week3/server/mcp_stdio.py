from __future__ import annotations

import json
import sys
from typing import Any

from .client import WeatherApiClient
from .config import Settings
from .errors import AppError, ToolNotFoundError, ValidationAppError
from .tools import ToolRegistry

SERVER_NAME = "week3-weather"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2025-06-18"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_current_weather",
        "description": "Get current weather for a city using Open-Meteo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Shanghai"}
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_forecast",
        "description": "Get daily forecast for a city (1-7 days).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Shanghai"},
                "days": {
                    "type": "integer",
                    "description": "Forecast days (1-7).",
                    "minimum": 1,
                    "maximum": 7,
                    "default": 3,
                },
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
]


def _jsonrpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _map_app_error(exc: AppError) -> tuple[int, str]:
    if isinstance(exc, ValidationAppError):
        return -32602, str(exc)
    if isinstance(exc, ToolNotFoundError):
        return -32601, str(exc)
    return -32000, str(exc)


def handle_message(message: dict[str, Any], registry: ToolRegistry) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    # Notifications do not require a response.
    if request_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None

    if method == "initialize":
        return _jsonrpc_result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "capabilities": {"tools": {}},
            },
        )

    if method == "ping":
        return _jsonrpc_result(request_id, {})

    if method == "tools/list":
        return _jsonrpc_result(request_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(tool_name, str) or not isinstance(arguments, dict):
            return _jsonrpc_error(request_id, -32602, "Invalid tools/call params")

        try:
            tool_result = registry.call(tool_name, arguments)
        except AppError as exc:
            code, message = _map_app_error(exc)
            return _jsonrpc_error(request_id, code, message, data={"tool": tool_name})
        except Exception:  # noqa: BLE001
            return _jsonrpc_error(request_id, -32603, "Internal server error")

        payload = tool_result.get("result", {})
        return _jsonrpc_result(
            request_id,
            {
                "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=True)}],
                "structuredContent": payload,
                "isError": False,
            },
        )

    return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")


def main() -> int:
    settings = Settings.from_env()
    registry = ToolRegistry(client=WeatherApiClient(settings=settings))

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                response = _jsonrpc_error(None, -32600, "Invalid Request")
            else:
                response = handle_message(message, registry)
        except json.JSONDecodeError:
            response = _jsonrpc_error(None, -32700, "Parse error")

        if response is not None:
            # Why: for STDIO transports, any non-protocol bytes on stdout can
            # break the client parser, so responses must be strict JSON only.
            print(json.dumps(response, ensure_ascii=True), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

