import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")

STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
}


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(400, "bad_request", message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(401, "unauthorized", message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Not allowed"):
        super().__init__(403, "forbidden", message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found"):
        super().__init__(404, "not_found", message)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(409, "conflict", message)


def error_body(code: str, message: str, details: list | None = None) -> dict:
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code, content=error_body(exc.code, exc.message)
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(request: Request, exc: StarletteHTTPException):
        code = STATUS_CODES.get(exc.status_code, "http_error")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_body(code, str(exc.detail)),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        details = [
            {"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content=error_body("validation_error", "Invalid request data", details),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.error("unhandled_error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=error_body("internal_error", "Something went wrong"),
        )
