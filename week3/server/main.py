from __future__ import annotations

import json
import sys

from pydantic import ValidationError

from .client import WeatherApiClient
from .config import Settings
from .errors import build_error_response
from .schemas import ToolCallRequest
from .tools import ToolRegistry


def handle_line(line: str, registry: ToolRegistry) -> dict:
    payload = json.loads(line)
    request = ToolCallRequest.model_validate(payload)
    data = registry.call(request.tool, request.arguments)
    return {"ok": True, "data": data}


def main() -> int:
    settings = Settings.from_env()
    registry = ToolRegistry(client=WeatherApiClient(settings=settings))

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        try:
            response = handle_line(line, registry)
        except json.JSONDecodeError as exc:
            response = build_error_response(exc).__dict__
            response["error"]["code"] = "invalid_json"
            response["error"]["message"] = "Input must be valid JSON"
        except ValidationError as exc:
            response = build_error_response(exc).__dict__
            response["error"]["code"] = "validation_error"
            response["error"]["message"] = str(exc)
        except Exception as exc:  # noqa: BLE001
            response = build_error_response(exc).__dict__

        # Why: STDIO transport requires protocol output on stdout; any debug logs
        # would corrupt the stream, so we only emit strict JSON responses.
        print(json.dumps(response, ensure_ascii=True), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
