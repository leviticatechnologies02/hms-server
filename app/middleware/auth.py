from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from typing import Optional
from jose import JWTError
from ..core.security import decode_token
from ..core.exceptions import UnauthorizedException
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for validating JWT tokens."""
    
    EXEMPT_PATHS = [
        "/health",
        "/",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/verify-otp"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            # Allow the request to continue, individual endpoints will handle auth
            return await call_next(request)
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise UnauthorizedException("Invalid authorization scheme")
            
            # Validate token
            payload = decode_token(token)
            
            # Check if token is access token
            if payload.get("type") != "access":
                raise UnauthorizedException("Invalid token type")
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            request.state.hospital_id = payload.get("hospital_id")
            request.state.permissions = payload.get("permissions", [])
            
        except (JWTError, ValueError, UnauthorizedException) as e:
            # Log the error but don't block the request
            logger.warning(f"Auth middleware error: {str(e)}")
            # Let the endpoint handle the authentication requirement
        
        return await call_next(request)