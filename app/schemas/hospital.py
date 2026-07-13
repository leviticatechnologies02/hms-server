from pydantic import BaseModel, Field, UUID4, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime
from .common import AuditMixinSchema, SoftDeleteMixinSchema


class HospitalBase(BaseModel):
    """Base hospital schema."""
    name: str = Field(..., min_length=2, max_length=255, description="Hospital name")
    code: str = Field(..., min_length=2, max_length=50, description="Unique hospital code")
    email: EmailStr = Field(..., description="Hospital email")
    phone: str = Field(..., min_length=10, max_length=20, description="Hospital phone")
    address: Optional[str] = Field(None, description="Hospital address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    pin_code: Optional[str] = Field(None, max_length=20, description="PIN code")
    timezone: Optional[str] = Field("UTC", description="Timezone")
    currency: Optional[str] = Field("INR", min_length=3, max_length=3, description="Currency code")
    settings: Optional[Dict[str, Any]] = Field(default={}, description="Hospital settings")
    meta_data: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class HospitalCreate(HospitalBase):
    """Hospital creation schema."""
    pass


class HospitalUpdate(BaseModel):
    """Hospital update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    pin_code: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field("UTC")
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    settings: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class HospitalResponse(HospitalBase, AuditMixinSchema, SoftDeleteMixinSchema):
    """Hospital response schema."""
    id: UUID4 = Field(..., description="Hospital ID")
    is_active: bool = Field(True, description="Active status")
    
    class Config:
        from_attributes = True


class HospitalListResponse(BaseModel):
    """Hospital list response schema."""
    items: list[HospitalResponse]
    total: int
    page: int
    limit: int
    pages: int