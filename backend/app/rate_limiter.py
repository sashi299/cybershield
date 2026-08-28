import time
import os
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding window rate limiter middleware.

    Notes:
    - This is an in-memory rate limiter suitable for single-process development/demo.
    - For production multi-worker deployments, use Redis or Memcached as the backing store.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        # Read from environment or use default (60 requests per 60 seconds per IP)
        self.max_requests = int(os.getenv("RATE_LIMIT_PER_MINUTE", str(max_requests)))
        self.window_seconds = window_seconds
        self.request_history = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Exclude static/health routes if any
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # Safeguard: Limit maximum tracked IPs in memory
        MAX_TRACKED_IPS = 10000
        if len(self.request_history) > MAX_TRACKED_IPS:
            # Evict oldest entries
            oldest_ips = sorted(
                self.request_history.keys(),
                key=lambda ip: min(self.request_history[ip]) if self.request_history[ip] else 0
            )[:MAX_TRACKED_IPS // 2]
            for ip in oldest_ips:
                del self.request_history[ip]

        now = time.time()
        window_start = now - self.window_seconds

        # Clean old timestamps
        history = [ts for ts in self.request_history[client_ip] if ts > window_start]
        if not history:
            del self.request_history[client_ip]
        else:
            self.request_history[client_ip] = history

        if len(history) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - history[0])) if history else self.window_seconds
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Rate limit exceeded. Please try again later."},
                headers={"Retry-After": str(max(1, retry_after))}
            )

        self.request_history[client_ip].append(now)
        response = await call_next(request)
        remaining = max(0, self.max_requests - len(self.request_history[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
