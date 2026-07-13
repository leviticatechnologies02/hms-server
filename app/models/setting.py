from sqlalchemy import Boolean, Column, String, JSON, Text
from .base import BaseModel, AuditMixin


class SystemSetting(BaseModel, AuditMixin):
    """System setting model."""
    
    __tablename__ = "system_settings"
    
    key = Column(String(255), nullable=False, unique=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    is_public = Column(Boolean, default=False)