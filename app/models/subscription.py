from sqlalchemy import Boolean, Column, String, DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditMixin
import uuid


class SubscriptionPlan(BaseModel, AuditMixin):
    """Subscription plan model."""
    
    __tablename__ = "subscription_plans"
    
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="INR")
    duration_days = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    max_users = Column(String(20), nullable=False)
    max_storage_gb = Column(String(20), nullable=False)
    features = Column(JSON, default=[])
    meta_data = Column(JSON, default={})
    
    # Relations
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(BaseModel, AuditMixin):
    """Subscription model."""
    
    __tablename__ = "subscriptions"
    
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False, unique=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_trial = Column(Boolean, default=False)
    status = Column(String(50), default="active")  # active, expired, cancelled, suspended
    
    # Relations
    hospital = relationship("Hospital", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")