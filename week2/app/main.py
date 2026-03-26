from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import init_db
from .errors import register_exception_handlers
from .routers import action_items, notes


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 应用启动时初始化数据库表；关闭时当前项目无额外清理动作。
    init_db()
    yield


def create_app() -> FastAPI:
    # App Factory 模式：将应用构建过程集中，便于测试和后续扩展。
    settings = get_settings()
    app = FastAPI(title=settings.app_title, lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        # 直接返回前端页面，方便同一服务同时提供 API 与简单 UI。
        html_path = settings.frontend_dir / "index.html"
        return html_path.read_text(encoding="utf-8")

    # 注册业务路由。
    app.include_router(notes.router)
    app.include_router(action_items.router)
    # 提供静态资源（JS/CSS）。
    app.mount("/static", StaticFiles(directory=str(settings.frontend_dir)), name="static")
    # 注册统一错误处理器，让返回格式一致。
    register_exception_handlers(app)
    return app


# 模块级 app 变量供 uvicorn 启动时导入。
app = create_app()
