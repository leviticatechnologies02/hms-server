from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditMixin

class CorporateReport(BaseModel, AuditMixin):
    """
    Corporate Reports
    Generated reports for Corporate Admin.
    """
    __tablename__ = "corporate_reports"

    # Relationships
    corporate_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("corporate_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    # Report Details
    title = Column(
        String(255),
        nullable=False,
    )
    report_type = Column(
        String(100),
        nullable=False,
        index=True,
    )
    report_code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    description = Column(
        Text,
        nullable=True,
    )

    # Report Filters
    from_date = Column(
        DateTime,
        nullable=True,
    )

    to_date = Column(
        DateTime,
        nullable=True,
    )

    file_name = Column(
        String(255),
        nullable=True,
    )

    file_path = Column(
        String(1000),
        nullable=True,
    )
    file_size = Column(
        Integer,
        default=0,
    )
    file_format = Column(
        String(20),
        default="pdf",
    )
    # Report Status
    status = Column(
        String(30),
        default="PENDING",
        index=True,
    )

    progress = Column(
        Integer,
        default=0,
    )
    is_downloaded = Column(
        Boolean,
        default=False,
    )
    download_count = Column(
        Integer,
        default=0,
    )
    last_downloaded_at = Column(
        DateTime,
        nullable=True,
    )
    expires_at = Column(
        DateTime,
        nullable=True,
    )
    error_message = Column(
        Text,
        nullable=True,
    )
    is_active = Column(
        Boolean,
        default=True,
    )

    # Relationships
    corporate_account = relationship(
        "CorporateAccount",
        back_populates="reports",
    )

    generated_user = relationship(
        "User",
        foreign_keys=[generated_by],
    )

    # Helper Methods
    @property
    def is_completed(self):
        return self.status == "COMPLETED"

    @property
    def is_failed(self):
        return self.status == "FAILED"

    @property
    def is_pending(self):
        return self.status == "PENDING"

    @property
    def can_download(self):
        return (
            self.status == "COMPLETED"
            and self.file_path is not None
        )

    def __repr__(self):
        return (
            f"<CorporateReport("
            f"title={self.title}, "
            f"type={self.report_type}, "
            f"status={self.status})>"
        )