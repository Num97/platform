import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.core.config import settings
from app.routes import proxy
from app.middleware.rate_limit import rate_limit_middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    logger.info(f"Gateway {request_id}: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Gateway-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"Gateway {request_id}: {response.status_code} ({process_time:.3f}s)"
        )
        return response
    except Exception as e:
        logger.error(f"Gateway error {request_id}: {str(e)}")
        return JSONResponse(
            status_code=500, content={"detail": "Gateway internal error"}
        )


app.middleware("http")(rate_limit_middleware)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": settings.VERSION,
        "timestamp": time.time(),
    }


@app.get("/")
async def root():
    return {
        "service": "api-gateway",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


app.include_router(proxy.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.GATEWAY_HOST,
        port=settings.GATEWAY_PORT,
        reload=settings.DEBUG
    )
