from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin, AuditMixin
import uuid


class Hospital(BaseModel, SoftDeleteMixin, AuditMixin):
    """Hospital model."""
    
    __tablename__ = "hospitals"
    
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pin_code = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    currency = Column(String(3), default="INR")
    
    # Settings
    settings = Column(JSON, default={})
    meta_data = Column(JSON, default={})
    
    # Relations
    subscription = relationship("Subscription", back_populates="hospital", uselist=False)
    users = relationship("User", back_populates="hospital")
    #departments = relationship("Department", back_populates="hospital")
    
    def __repr__(self):
        return f"<Hospital {self.name}>"