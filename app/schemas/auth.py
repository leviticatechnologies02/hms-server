from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Token expiry in seconds")
    role: str = Field(..., description="User role")
    user_id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str = Field(..., description="New JWT access token")
    expires_in: int = Field(..., description="Token expiry in seconds")


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""
    email: EmailStr = Field(..., description="Registered email")


class VerifyOTPRequest(BaseModel):
    """Verify OTP request schema."""
    email: EmailStr = Field(..., description="Registered email")
    otp: str = Field(..., min_length=6, max_length=6, description="OTP received")


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""
    email: EmailStr = Field(..., description="Registered email")
    new_password: str = Field(..., min_length=12, description="New password")
    
    @validator('new_password')
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


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=12, description="New password")
    
    @validator('new_password')
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


class SessionResponse(BaseModel):
    """Session validation response schema."""
    user_id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Session active status")


class UserProfileResponse(BaseModel):
    """User profile response schema."""
    id: str = Field(..., description="User ID")
    full_name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email")
    username: str = Field(..., description="Username")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    hospital_id: Optional[str] = Field(None, description="Hospital ID")
    is_active: bool = Field(..., description="Active status")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    created_at: datetime = Field(..., description="Account creation time")


class LoginHistoryItem(BaseModel):
    """Login history item schema."""
    timestamp: datetime = Field(..., description="Login timestamp")
    action: str = Field(..., description="Action performed")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    status: str = Field(..., description="Status")


class LoginHistoryResponse(BaseModel):
    """Login history response schema."""
    history: List[LoginHistoryItem] = Field(..., description="Login history list")