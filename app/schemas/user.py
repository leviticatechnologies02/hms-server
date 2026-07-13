from pydantic import BaseModel, Field, EmailStr, UUID4, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common import AuditMixinSchema, SoftDeleteMixinSchema


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Phone number")
    user_type: str = Field(..., description="User type: platform_user, hospital_user, patient")
    hospital_id: Optional[UUID4] = Field(None, description="Hospital ID")
    role_name: str = Field(..., description="Primary role name")
    language: Optional[str] = Field("en", description="Language preference")
    timezone: Optional[str] = Field("UTC", description="Timezone")
    preferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")


class PlatformUserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None
    password: str = Field(..., min_length=12, description="Password")
    role_name: str = "super_admin"
    role_id: Optional[UUID4] = None
    language: str = "en"
    timezone: str = "UTC"
    preferences: Dict[str, Any] = {}

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in "!@#$%^&*()" for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=12, description="Password")
    role_id: Optional[UUID4] = Field(None, description="Role ID")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in "!@#$%^&*()" for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    hospital_id: Optional[UUID4] = None
    role_name: Optional[str] = None
    role_id: Optional[UUID4] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase, AuditMixinSchema, SoftDeleteMixinSchema):
    """User response schema."""
    id: UUID4 = Field(..., description="User ID")
    is_active: bool = Field(True, description="Active status")
    is_verified: bool = Field(False, description="Verified status")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    password_changed_at: Optional[datetime] = Field(None, description="Password last changed")
    
    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """User profile schema with additional details."""
    roles: List[str] = Field(default=[], description="User roles")
    permissions: List[str] = Field(default=[], description="User permissions")
    hospital_name: Optional[str] = Field(None, description="Hospital name")


class UserListResponse(BaseModel):
    """User list response schema."""
    items: List[UserResponse]
    total: int
    page: int
    limit: int
    pages: int


class UserRoleAssignment(BaseModel):
    """User role assignment schema."""
    user_id: UUID4 = Field(..., description="User ID")
    role_id: UUID4 = Field(..., description="Role ID")


class UserBulkCreate(BaseModel):
    """Bulk user creation schema."""
    users: List[UserCreate] = Field(..., description="List of users to create")
    default_role_id: Optional[UUID4] = Field(None, description="Default role ID")


class UserBulkResponse(BaseModel):
    """Bulk user creation response."""
    created: List[UserResponse] = Field(..., description="Created users")
    failed: List[Dict[str, Any]] = Field(..., description="Failed creations")
    total_created: int = Field(..., description="Total created")
    total_failed: int = Field(..., description="Total failed")