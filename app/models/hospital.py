from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey
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
    # Corporate Account
    corporate_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("corporate_accounts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Hospital Group
    hospital_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hospital_groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Settings
    settings = Column(JSON, default={})
    meta_data = Column(JSON, default={})
    
    # Relations
    subscription = relationship("Subscription", back_populates="hospital", uselist=False)
    users = relationship("User", back_populates="hospital")
    #departments = relationship("Department", back_populates="hospital")
    corporate_account = relationship(
        "CorporateAccount",
        back_populates="hospitals",
    )

    hospital_group = relationship(
        "HospitalGroup",
        back_populates="hospitals",
    )
    
    def __repr__(self):
        return f"<Hospital {self.name}>"