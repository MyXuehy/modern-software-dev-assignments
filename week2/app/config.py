from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    # 应用显示名称（用于 FastAPI 文档标题等场景）
    app_title: str
    # 前端静态页面所在目录（index.html、js、css 都在这里）
    frontend_dir: Path


@lru_cache
def get_settings() -> Settings:
    # 统一读取配置，避免在各个文件里重复拼路径/读环境变量。
    # lru_cache 可以让这个函数只在首次调用时执行一次，提高效率。
    base_dir = Path(__file__).resolve().parents[1]
    frontend_dir = base_dir / "frontend"
    return Settings(
        # 支持通过环境变量覆盖标题；未设置时使用默认值。
        app_title=os.getenv("APP_TITLE", "Action Item Extractor"),
        frontend_dir=frontend_dir,
    )

