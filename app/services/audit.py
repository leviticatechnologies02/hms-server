from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from ..repositories.audit import AuditRepository
from ..schemas.audit import AuditLogResponse
from ..core.exceptions import NotFoundException


class AuditService:
    """Audit service."""
    
    def __init__(self, db: Session):
        self.audit_repo = AuditRepository(db)
        self.db = db
    
    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[AuditLogResponse], int]:
        """Get audit logs with filters."""
        query = self.db.query(self.audit_repo.model)
        
        if user_id:
            query = query.filter(self.audit_repo.model.user_id == user_id)
        if action:
            query = query.filter(self.audit_repo.model.action == action)
        if resource_type:
            query = query.filter(self.audit_repo.model.resource_type == resource_type)
        if start_date:
            query = query.filter(self.audit_repo.model.created_at >= start_date)
        if end_date:
            query = query.filter(self.audit_repo.model.created_at <= end_date)
        
        total = query.count()
        logs = query.order_by(self.audit_repo.model.created_at.desc()).offset(skip).limit(limit).all()
        
        return [AuditLogResponse.model_validate(log) for log in logs], total
    
    def get_user_audit_logs(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLogResponse]:
        """Get audit logs for a specific user."""
        logs = self.audit_repo.get_by_user(user_id, skip, limit)
        return [AuditLogResponse.model_validate(log) for log in logs]
    
    def get_resource_audit_logs(self, resource_type: str, resource_id: UUID) -> List[AuditLogResponse]:
        """Get audit logs for a specific resource."""
        logs = self.audit_repo.get_by_resource(resource_type, resource_id)
        return [AuditLogResponse.model_validate(log) for log in logs]