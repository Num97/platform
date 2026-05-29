import time
import threading
from collections import defaultdict
from fastapi import Request, HTTPException

from app.core.config import settings


class RateLimitMiddleware:
    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    async def __call__(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW
        max_requests = settings.RATE_LIMIT_REQUESTS

        with self._lock:
            self._requests[client_ip] = [
                t for t in self._requests[client_ip] if now - t < window
            ]

            if len(self._requests[client_ip]) >= max_requests:
                raise HTTPException(status_code=429, detail="Too many requests")

            self._requests[client_ip].append(now)

        return await call_next(request)


rate_limit_middleware = RateLimitMiddleware()
