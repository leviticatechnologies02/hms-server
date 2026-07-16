from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.audit import AuditRepository
from ..schemas.audit import AuditLogResponse


class AuditService:
    """Audit service."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditRepository(db)

    async def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[AuditLogResponse], int]:
        """Get audit logs with filters."""

        query = select(self.audit_repo.model)

        if user_id:
            query = query.where(self.audit_repo.model.user_id == user_id)

        if action:
            query = query.where(self.audit_repo.model.action == action)

        if resource_type:
            query = query.where(self.audit_repo.model.resource_type == resource_type)

        if start_date:
            query = query.where(self.audit_repo.model.created_at >= start_date)

        if end_date:
            query = query.where(self.audit_repo.model.created_at <= end_date)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query)

        query = (
            query.order_by(self.audit_repo.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return (
            [AuditLogResponse.model_validate(log) for log in logs],
            total or 0,
        )

    async def get_user_audit_logs(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLogResponse]:
        """Get audit logs for a specific user."""

        logs = await self.audit_repo.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        return [
            AuditLogResponse.model_validate(log)
            for log in logs
        ]

    async def get_resource_audit_logs(
        self,
        resource_type: str,
        resource_id: UUID,
    ) -> List[AuditLogResponse]:
        """Get audit logs for a specific resource."""

        logs = await self.audit_repo.get_by_resource(
            resource_type=resource_type,
            resource_id=resource_id,
        )

        return [
            AuditLogResponse.model_validate(log)
            for log in logs
        ]