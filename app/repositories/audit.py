from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List
from uuid import UUID

from ..models.audit import AuditLog
from .base import BaseRepository


class AuditRepository(BaseRepository):
    """Audit log repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AuditLog)

    async def get_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs by user."""

        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: UUID,
    ) -> List[AuditLog]:
        """Get audit logs by resource."""

        result = await self.db.execute(
            select(AuditLog)
            .where(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.created_at.desc())
        )

        return result.scalars().all()

    async def get_by_hospital(
        self,
        hospital_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs by hospital."""

        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.hospital_id == hospital_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Get audit logs by action."""

        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[AuditLog]:
        """Get audit logs within date range."""

        result = await self.db.execute(
            select(AuditLog)
            .where(
                AuditLog.created_at.between(start_date, end_date)
            )
            .order_by(AuditLog.created_at.desc())
        )

        return result.scalars().all()

    async def get_latest_for_user(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> List[AuditLog]:
        """Get latest audit logs for user."""

        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()