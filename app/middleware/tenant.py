from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..models.hospital import Hospital
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """Tenant isolation middleware for multi-tenant architecture."""
    
    EXEMPT_PATHS = [
        "/health", "/", "/api/docs", "/api/redoc", "/api/openapi.json",
        "/api/v1/auth/login", "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password", "/api/v1/auth/reset-password",
        "/api/v1/auth/verify-otp"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Check if endpoint requires hospital context
        if self.requires_hospital_context(request.url.path):
            hospital_id = request.headers.get("Hospital-ID")
            
            if not hospital_id:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "message": "Hospital-ID header is required",
                        "error_code": "HOSPITAL_ID_REQUIRED"
                    }
                )
            
            # Validate hospital exists and is active
            db = SessionLocal()
            try:
                hospital = db.query(Hospital).filter(
                    Hospital.id == hospital_id,
                    Hospital.is_active == True,
                    Hospital.is_deleted == False
                ).first()
                
                if not hospital:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={
                            "success": False,
                            "message": "Invalid or inactive hospital",
                            "error_code": "INVALID_HOSPITAL"
                        }
                    )
                
                # Store hospital in request state
                request.state.hospital = hospital
                
            finally:
                db.close()
        
        return await call_next(request)
    
    def requires_hospital_context(self, path: str) -> bool:
        """Check if endpoint requires hospital context."""
        # Super admin endpoints don't require hospital context
        if "/super-admin/" in path:
            return False
        
        # Hospital admin endpoints require hospital context
        if "/hospital-admin/" in path:
            return True
        
        # Patient/clinical endpoints require hospital context
        clinical_paths = [
            "/patients", "/doctors", "/appointments", "/emr",
            "/lab-orders", "/radiology-orders", "/prescriptions",
            "/billing", "/inventory", "/admissions"
        ]
        
        for clinical_path in clinical_paths:
            if clinical_path in path:
                return True
        
        return False