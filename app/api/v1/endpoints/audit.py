from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.schemas.audit import AuditLogResponse

from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....schemas.common import ResponseModel
from ....services.audit import AuditService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/audit-logs",
    tags=["Super Admin - Audit Logs"]
)


@router.get(
    "/",
    response_model=ResponseModel,
    summary="Get Audit Logs",
    description="Get all audit logs with filters"
)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db)

    skip = (page - 1) * limit

    logs, total = await service.get_audit_logs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
    )

    return ResponseModel(
        success=True,
        message="Audit logs retrieved successfully",
        data={
            "items": [AuditLogResponse.model_validate(log).model_dump() for log in logs],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 0,
        },
    )


@router.get(
    "/user/{user_id}",
    response_model=ResponseModel,
    summary="Get User Audit Logs",
    description="Get audit logs for a specific user"
)
async def get_user_audit_logs(
    user_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db)

    skip = (page - 1) * limit

    logs = await service.get_user_audit_logs(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    return ResponseModel(
        success=True,
        message="User audit logs retrieved successfully",
        data=[
            AuditLogResponse.model_validate(log).model_dump()
            for log in logs
        ],
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
    db: AsyncSession = Depends(get_db),
):
    service = AuditService(db)

    logs = await service.get_resource_audit_logs(
        resource_type=resource_type,
        resource_id=resource_id,
    )

    return ResponseModel(
        success=True,
        message="Resource audit logs retrieved successfully",
        data=[
            AuditLogResponse.model_validate(log).model_dump()
            for log in logs
        ],
    )