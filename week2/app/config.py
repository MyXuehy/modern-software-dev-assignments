from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_title: str
    frontend_dir: Path


@lru_cache
def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[1]
    frontend_dir = base_dir / "frontend"
    return Settings(
        app_title=os.getenv("APP_TITLE", "Action Item Extractor"),
        frontend_dir=frontend_dir,
    )

