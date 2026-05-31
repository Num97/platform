import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.config import settings
from app.core.dependencies import verify_token

router = APIRouter()

OPEN_ROUTES = {
    ("POST", "/api/v1/auth/login"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/logout"),
    ("POST", "/api/v1/auth/forgot-password"),
    ("POST", "/api/v1/auth/reset-password"),
}

SERVICE_ROUTES = {
    "/api/v1/auth": settings.AUTH_SERVICE_URL,
}


def _get_backend_url(path: str) -> Optional[str]:
    for prefix, service_url in SERVICE_ROUTES.items():
        if path.startswith(prefix):
            return service_url
    return None


async def _proxy_request(request: Request, backend_url: str, path: str):
    method = request.method
    url = f"{backend_url}{path}"
    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params,
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Backend service unavailable")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Backend service timeout")

    return StreamingResponse(
        content=response.aiter_bytes(),
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, path: str):
    full_path = f"/{path}"

    backend_url = _get_backend_url(full_path)
    if not backend_url:
        raise HTTPException(status_code=404, detail=f"No backend for path: {full_path}")

    route_key = (request.method, full_path)
    if route_key not in OPEN_ROUTES:
        verify_token(request.headers.get("authorization"))

    return await _proxy_request(request, backend_url, full_path)
