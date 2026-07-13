from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from ..models.audit import AuditLog
from .base import BaseRepository


class AuditRepository(BaseRepository):
    """Audit log repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, AuditLog)
    
    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_resource(self, resource_type: str, resource_id: UUID) -> List[AuditLog]:
        """Get audit logs by resource."""
        return self.db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).all()
    
    def get_by_hospital(self, hospital_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by hospital."""
        return self.db.query(AuditLog).filter(
            AuditLog.hospital_id == hospital_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_action(self, action: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action."""
        return self.db.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_date_range(self, start_date: datetime, end_date: datetime) -> List[AuditLog]:
        """Get audit logs within date range."""
        return self.db.query(AuditLog).filter(
            AuditLog.created_at.between(start_date, end_date)
        ).order_by(AuditLog.created_at.desc()).all()
    
    def get_latest_for_user(self, user_id: UUID, limit: int = 10) -> List[AuditLog]:
        """Get latest audit logs for user."""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()