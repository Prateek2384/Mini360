import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import setup_logging
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.assessments import router as assessments_router
from app.routes.self_assessment import router as self_assessment_router
from app.routes.invitations import router as invitations_router


setup_logging()
logger = logging.getLogger("app.request")

app = FastAPI(title="Mini 360 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid.uuid4().hex
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    route = request.scope.get("route")
    logger.info(
        "request",
        extra={
            "extra_fields": {
                "request_id": request_id,
                "method": request.method,
                "path": getattr(route, "path", "unmatched"),
                "status": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


register_error_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(assessments_router)
app.include_router(self_assessment_router)
app.include_router(invitations_router)
