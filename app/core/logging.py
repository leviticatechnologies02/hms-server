from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Any, Dict
from ..models.audit import AuditLog
import logging

logger = logging.getLogger(__name__)


def create_audit_log(
    db: Session,
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
    hospital_id: Optional[UUID] = None
) -> AuditLog:
    """Create an audit log entry."""
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
            hospital_id=hospital_id
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")
        db.rollback()
        # Don't raise the exception to prevent disrupting the main flow
        return None