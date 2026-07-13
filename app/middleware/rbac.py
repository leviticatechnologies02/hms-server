from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import List, Optional
from ..core.exceptions import ForbiddenException
import logging

logger = logging.getLogger(__name__)


class RBACMiddleware(BaseHTTPMiddleware):
    """RBAC middleware for permission checking."""
    
    # Define permission requirements for endpoints
    PERMISSION_MAP = {
        "/api/v1/super-admin/hospitals": {
            "GET": "hospital.read",
            "POST": "hospital.create",
            "PUT": "hospital.update",
            "DELETE": "hospital.delete"
        },
        "/api/v1/super-admin/subscriptions": {
            "GET": "subscription.read",
            "POST": "subscription.create",
            "PUT": "subscription.update",
            "DELETE": "subscription.delete"
        },
        "/api/v1/super-admin/audit-logs": {
            "GET": "audit.read"
        },
        "/api/v1/super-admin/users": {
            "GET": "user.read",
            "POST": "user.create",
            "PUT": "user.update",
            "DELETE": "user.delete"
        }
    }
    
    async def dispatch(self, request: Request, call_next):
        # Skip for exempt paths
        exempt_paths = [
            "/health", "/", "/api/docs", "/api/redoc", 
            "/api/openapi.json", "/api/v1/auth/login",
            "/api/v1/auth/refresh"
        ]
        
        if request.url.path in exempt_paths:
            return await call_next(request)
        
        # Check if endpoint has permission requirements
        permission = self.get_required_permission(request)
        
        if permission:
            # Check if user has the required permission
            user_permissions = getattr(request.state, "permissions", [])
            
            # Super admin check (handled in endpoint)
            if "super_admin" == getattr(request.state, "user_role", ""):
                return await call_next(request)
            
            if permission not in user_permissions:
                logger.warning(f"Permission denied: {permission} for user {getattr(request.state, 'user_id', 'unknown')}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "success": False,
                        "message": f"Permission '{permission}' required",
                        "error_code": "FORBIDDEN"
                    }
                )
        
        return await call_next(request)
    
    def get_required_permission(self, request: Request) -> Optional[str]:
        """Get required permission for the request path and method."""
        path = request.url.path
        method = request.method
        
        # Find matching permission
        for endpoint_path, methods in self.PERMISSION_MAP.items():
            if path.startswith(endpoint_path) or path == endpoint_path:
                if method in methods:
                    return methods[method]
        
        return None