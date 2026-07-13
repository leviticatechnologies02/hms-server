from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime
from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....schemas.audit import AuditLogResponse
from ....schemas.common import ResponseModel
from ....services.audit import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit-logs", tags=["Super Admin - Audit Logs"])


@router.get(
    "/",
    response_model=ResponseModel,
    summary="Get Audit Logs",
    description="Get all audit logs with filters"
)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with filters."""
    service = AuditService(db)
    skip = (page - 1) * limit
    logs, total = service.get_audit_logs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date
    )
    
    return ResponseModel(
        success=True,
        message="Audit logs retrieved successfully",
        data={
            "items": [log.model_dump() for log in logs],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    )


@router.get(
    "/user/{user_id}",
    response_model=ResponseModel,
    summary="Get User Audit Logs",
    description="Get audit logs for a specific user"
)
async def get_user_audit_logs(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific user."""
    service = AuditService(db)
    skip = (page - 1) * limit
    logs = service.get_user_audit_logs(user_id, skip, limit)
    
    return ResponseModel(
        success=True,
        message="User audit logs retrieved successfully",
        data=[log.model_dump() for log in logs]
    )


@router.get(
    "/resource/{resource_type}/{resource_id}",
    response_model=ResponseModel,
    summary="Get Resource Audit Logs",
    description="Get audit logs for a specific resource"
)
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific resource."""
    service = AuditService(db)
    logs = service.get_resource_audit_logs(resource_type, resource_id)
    
    return ResponseModel(
        success=True,
        message="Resource audit logs retrieved successfully",
        data=[log.model_dump() for log in logs]
    )