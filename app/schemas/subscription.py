from pydantic import BaseModel, Field, UUID4, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common import AuditMixinSchema


class SubscriptionPlanBase(BaseModel):
    """Base subscription plan schema."""
    name: str = Field(..., min_length=2, max_length=100, description="Plan name")
    code: str = Field(..., min_length=2, max_length=50, description="Unique plan code")
    description: Optional[str] = Field(None, max_length=500, description="Plan description")
    price: float = Field(..., gt=0, description="Plan price")
    currency: str = Field("INR", min_length=3, max_length=3, description="Currency")
    duration_days: str = Field(..., description="Duration: monthly, quarterly, yearly")
    max_users: int = Field(..., gt=0, description="Maximum users")
    max_storage_gb: int = Field(..., gt=0, description="Maximum storage in GB")
    features: List[str] = Field(default=[], description="Plan features")
    meta_data: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Subscription plan creation schema."""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Subscription plan update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    duration_days: Optional[str] = None
    max_users: Optional[int] = Field(None, gt=0)
    max_storage_gb: Optional[int] = Field(None, gt=0)
    features: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase, AuditMixinSchema):
    """Subscription plan response schema."""
    id: UUID4 = Field(..., description="Plan ID")
    is_active: bool = Field(True, description="Active status")
    
    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    hospital_id: UUID4 = Field(..., description="Hospital ID")
    plan_id: UUID4 = Field(..., description="Plan ID")
    start_date: datetime = Field(..., description="Subscription start date")
    end_date: datetime = Field(..., description="Subscription end date")
    is_trial: bool = Field(False, description="Trial subscription")
    status: str = Field("active", description="Subscription status")


class SubscriptionCreate(SubscriptionBase):
    """Subscription creation schema."""
    pass


class SubscriptionUpdate(BaseModel):
    """Subscription update schema."""
    plan_id: Optional[UUID4] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_trial: Optional[bool] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase, AuditMixinSchema):
    """Subscription response schema."""
    id: UUID4 = Field(..., description="Subscription ID")
    is_active: bool = Field(True, description="Active status")
    
    class Config:
        from_attributes = True