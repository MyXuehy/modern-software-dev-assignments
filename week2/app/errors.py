from __future__ import annotations

import logging
import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class NotFoundError(Exception):
    # 用于表示“资源不存在”，由统一异常处理器转成 HTTP 404。
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class BadRequestError(Exception):
    # 用于表示“请求参数或业务条件不合法”，转成 HTTP 400。
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def register_exception_handlers(app: FastAPI) -> None:
    # 集中注册异常处理，避免每个路由手写重复 try/except。
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(BadRequestError)
    async def bad_request_handler(_: Request, exc: BadRequestError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(sqlite3.Error)
    async def sqlite_error_handler(_: Request, exc: sqlite3.Error) -> JSONResponse:
        # 数据库异常只向客户端暴露通用信息，详细栈写入日志，减少敏感信息泄露。
        logger.exception("Database error", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "database error"})
