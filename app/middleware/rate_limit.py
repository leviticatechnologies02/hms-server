from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse."""
    
    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.limit_per_minute = 60
        self.limit_per_day = 1000
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for certain paths
        exempt_paths = ["/health", "/", "/api/docs", "/api/redoc"]
        if request.url.path in exempt_paths:
            return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self.get_client_id(request)
        
        # Check rate limit
        if not self.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            )
        
        return await call_next(request)
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier."""
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request."""
        now = time.time()
        
        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id] 
            if t > now - 86400  # Keep last 24 hours
        ]
        
        # Check per-minute limit
        minute_ago = now - 60
        minute_requests = len([t for t in self.requests[client_id] if t > minute_ago])
        
        if minute_requests >= self.limit_per_minute:
            return False
        
        # Check per-day limit
        day_ago = now - 86400
        day_requests = len([t for t in self.requests[client_id] if t > day_ago])
        
        if day_requests >= self.limit_per_day:
            return False
        
        # Allow request and log it
        self.requests[client_id].append(now)
        return True