from pydantic import BaseModel, Field, UUID4
from typing import Optional, Any, Dict
from datetime import datetime


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    user_id: Optional[UUID4] = None
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Resource type")
    resource_id: Optional[UUID4] = None
    resource_data: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str = Field("success", description="Status of action")
    error_message: Optional[str] = None
    hospital_id: Optional[UUID4] = None


class AuditLogResponse(AuditLogBase):
    """Audit log response schema."""
    id: UUID4 = Field(..., description="Audit log ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True