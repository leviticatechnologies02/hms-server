# app/core/logging.py

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit import AuditLog

logger = logging.getLogger(__name__)


async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[UUID] = None,
    resource_data: Optional[Dict[str, Any]] = None,
    changes: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    hospital_id: Optional[UUID] = None,
) -> Optional[AuditLog]:
    """
    Create Audit Log
    """

    try:

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_data=resource_data,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
            hospital_id=hospital_id,
        )

        db.add(audit_log)

        await db.commit()

        await db.refresh(audit_log)

        return audit_log

    except Exception as e:

        logger.exception(
            "Failed to create audit log: %s",
            str(e),
        )

        await db.rollback()

        return None