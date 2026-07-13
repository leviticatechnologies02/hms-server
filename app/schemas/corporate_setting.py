from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Create
class CorporateSettingCreate(BaseModel):
    corporate_account_id: UUID
    timezone: str = "Asia/Kolkata"
    language: str = "en"
    currency: str = "INR"
    date_format: str = "DD-MM-YYYY"
    time_format: str = "24H"
    dashboard_refresh_interval: int = 30
    dashboard_theme: str = "LIGHT"
    default_dashboard: str = "overview"
    default_report_format: str = "PDF"
    auto_generate_reports: bool = False
    report_retention_days: int = 365
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    notification_preferences: dict = {}
    session_timeout: int = 30
    mfa_enabled: bool = False
    password_expiry_days: int = 90
    allow_multiple_sessions: bool = False
    enable_audit_logs: bool = True
    audit_retention_days: int = 365

# Update
class CorporateSettingUpdate(BaseModel):
    timezone: Optional[str] = None
    language: Optional[str] = None
    currency: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    dashboard_refresh_interval: Optional[int] = None
    dashboard_theme: Optional[str] = None
    default_dashboard: Optional[str] = None
    default_report_format: Optional[str] = None
    auto_generate_reports: Optional[bool] = None
    report_retention_days: Optional[int] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    notification_preferences: Optional[dict] = None
    session_timeout: Optional[int] = None
    mfa_enabled: Optional[bool] = None
    password_expiry_days: Optional[int] = None
    allow_multiple_sessions: Optional[bool] = None
    enable_audit_logs: Optional[bool] = None
    audit_retention_days: Optional[int] = None
    is_active: Optional[bool] = None

# Response
class CorporateSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    corporate_account_id: UUID
    timezone: str
    language: str
    currency: str
    date_format: str
    time_format: str
    dashboard_refresh_interval: int
    dashboard_theme: str
    default_dashboard: str
    default_report_format: str
    auto_generate_reports: bool
    report_retention_days: int
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    notification_preferences: dict
    session_timeout: int
    session_timeout_seconds: int
    mfa_enabled: bool
    password_expiry_days: int
    allow_multiple_sessions: bool
    enable_audit_logs: bool
    audit_retention_days: int
    is_active: bool
    created_at: datetime
    updated_at: datetime