from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..core.logging import create_audit_log
import logging
import json
from uuid import UUID

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware for tracking API requests."""
    
    EXCLUDED_PATHS = [
        "/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json"
    ]
    
    EXCLUDED_METHODS = ["OPTIONS"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip for excluded paths
        if request.url.path in self.EXCLUDED_PATHS or request.method in self.EXCLUDED_METHODS:
            return await call_next(request)
        
        # Get request details
        user_id = getattr(request.state, "user_id", None)
        hospital_id = getattr(request.state, "hospital_id", None)
        
        # Get IP address
        ip_address = request.client.host if request.client else None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()
        
        # Get user agent
        user_agent = request.headers.get("User-Agent")
        
        # Process the request
        response = await call_next(request)
        
        # Log the request asynchronously
        try:
            db = SessionLocal()
            
            # Extract request body for audit (only for create/update operations)
            resource_data = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        resource_data = json.loads(body)
                except:
                    pass
            
            # Determine action based on HTTP method
            action_map = {
                "GET": "read",
                "POST": "create",
                "PUT": "update",
                "PATCH": "patch",
                "DELETE": "delete"
            }
            
            action = action_map.get(request.method, "unknown")
            resource_type = self.extract_resource_type(request.url.path)
            
            # Create audit log
            create_audit_log(
                db=db,
                user_id=user_id,
                action=f"{action}_{resource_type}" if resource_type else action,
                resource_type=resource_type or "unknown",
                resource_data=resource_data,
                ip_address=ip_address,
                user_agent=user_agent,
                status="success" if response.status_code < 400 else "error",
                hospital_id=hospital_id
            )
            db.close()
            
        except Exception as e:
            logger.error(f"Audit middleware error: {str(e)}")
        
        return response
    
    def extract_resource_type(self, path: str) -> str:
        """Extract resource type from API path."""
        # Remove API version prefix
        parts = path.split("/")
        
        # Find the resource in the path
        for i, part in enumerate(parts):
            if part in ["super-admin", "hospital-admin"]:
                if i + 1 < len(parts):
                    return parts[i + 1]
        
        # Fallback: use last non-ID segment
        for part in reversed(parts):
            if part and not self.is_uuid(part) and part not in ["api", "v1"]:
                return part
        
        return "unknown"
    
    def is_uuid(self, value: str) -> bool:
        """Check if string is a UUID."""
        try:
            UUID(value)
            return True
        except ValueError:
            return False