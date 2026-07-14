from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import PlainTextResponse, Response


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.code = code
        super().__init__(status_code=status_code, detail=message)


def _is_api_path(request: Request) -> bool:
    return request.url.path.startswith("/api")


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.code, str(exc.detail)),
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> Response:
    # SQLAdmin(/admin) 등 HTML 라우트는 JSON 에러 형식을 쓰지 않음
    if not _is_api_path(request):
        return PlainTextResponse(
            str(exc.detail),
            status_code=exc.status_code,
            headers=getattr(exc, "headers", None),
        )

    if isinstance(exc.detail, dict) and "code" in exc.detail and "message" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    code = {
        status.HTTP_400_BAD_REQUEST: "VALIDATION_ERROR",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "DUPLICATE_STUDENT",
    }.get(exc.status_code, "INTERNAL_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, str(exc.detail)),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    if not _is_api_path(request):
        return PlainTextResponse(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = " -> ".join(str(part) for part in first.get("loc", []) if part != "body")
        msg = first.get("msg", "Validation failed")
        message = f"{loc}: {msg}" if loc else msg
    else:
        message = "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_body("VALIDATION_ERROR", message),
    )


async def unhandled_exception_handler(
    request: Request, _exc: Exception
) -> Response:
    if not _is_api_path(request):
        return PlainTextResponse(
            "Internal Server Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_body("INTERNAL_ERROR", "Internal server error"),
    )
