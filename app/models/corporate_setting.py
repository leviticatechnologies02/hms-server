from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel, AuditMixin


class CorporateSetting(BaseModel, AuditMixin):
    """
    Corporate level settings.

    One settings record per Corporate Account.
    """

    __tablename__ = "corporate_settings"

    # Relations
    corporate_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "corporate_accounts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # General
    timezone = Column(
        String(100),
        default="Asia/Kolkata",
    )

    language = Column(
        String(20),
        default="en",
    )

    currency = Column(
        String(10),
        default="INR",
    )

    date_format = Column(
        String(30),
        default="DD-MM-YYYY",
    )

    time_format = Column(
        String(20),
        default="24H",
    )

    # Dashboard
    dashboard_refresh_interval = Column(
        Integer,
        default=30,
    )

    dashboard_theme = Column(
        String(30),
        default="LIGHT",
    )

    default_dashboard = Column(
        String(100),
        default="overview",
    )

    # Reports
    default_report_format = Column(
        String(20),
        default="PDF",
    )

    auto_generate_reports = Column(
        Boolean,
        default=False,
    )

    report_retention_days = Column(
        Integer,
        default=365,
    )

    # Notifications
    email_notifications = Column(
        Boolean,
        default=True,
    )

    sms_notifications = Column(
        Boolean,
        default=False,
    )

    push_notifications = Column(
        Boolean,
        default=True,
    )

    notification_preferences = Column(
        JSON,
        default=dict,
    )

    # Security
    session_timeout = Column(
        Integer,
        default=30,
    )

    mfa_enabled = Column(
        Boolean,
        default=False,
    )

    password_expiry_days = Column(
        Integer,
        default=90,
    )

    allow_multiple_sessions = Column(
        Boolean,
        default=False,
    )

    # Audit
    enable_audit_logs = Column(
        Boolean,
        default=True,
    )

    audit_retention_days = Column(
        Integer,
        default=365,
    )

    # Status
    is_active = Column(
        Boolean,
        default=True,
    )

    # Relationships
    corporate_account = relationship(
        "CorporateAccount",
        back_populates="settings",
    )

    # Helpers
    @property
    def session_timeout_seconds(self):
        return self.session_timeout * 60

    def __repr__(self):
        return (
            f"<CorporateSetting("
            f"corporate={self.corporate_account_id})>"
        )