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
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_title, lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        html_path = settings.frontend_dir / "index.html"
        return html_path.read_text(encoding="utf-8")

    app.include_router(notes.router)
    app.include_router(action_items.router)
    app.mount("/static", StaticFiles(directory=str(settings.frontend_dir)), name="static")
    register_exception_handlers(app)
    return app


app = create_app()
