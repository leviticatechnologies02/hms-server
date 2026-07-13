import uuid
from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Text,
    Integer,
    Numeric,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel, AuditMixin


class CorporateAccount(BaseModel, AuditMixin):
    """
    Corporate Account

    One Corporate Account can manage multiple Hospital Groups.
    """

    __tablename__ = "corporate_accounts"

    # Basic Information
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)

    legal_name = Column(String(255), nullable=True)

    registration_number = Column(String(100), nullable=True)

    tax_number = Column(String(100), nullable=True)

    description = Column(Text, nullable=True)

    logo = Column(String(500), nullable=True)

    website = Column(String(255), nullable=True)

    # Contact
    email = Column(String(255), nullable=False)

    phone = Column(String(30), nullable=True)

    alternate_phone = Column(String(30), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Subscription / Limits
    max_hospitals = Column(Integer, default=1)
    max_branches = Column(Integer, default=1)
    max_users = Column(Integer, default=100)
    max_storage_gb = Column(Integer, default=100)
    current_storage_gb = Column(Numeric(10, 2), default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # Owner
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    # Relations
    owner = relationship(
        "User",
        foreign_keys=[owner_id],
    )
    hospital_groups = relationship(
        "HospitalGroup",
        back_populates="corporate_account",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "CorporateReport",
        back_populates="corporate_account",
        cascade="all, delete-orphan",
    )

    # Helper Methods
    @property
    def available_storage(self):
        return float(self.max_storage_gb) - float(self.current_storage_gb)

    @property
    def storage_usage_percentage(self):
        if self.max_storage_gb == 0:
            return 0
        return round(
            (float(self.current_storage_gb) / float(self.max_storage_gb)) * 100,
            2,
        )

    def __repr__(self):
        return (
            f"<CorporateAccount("
            f"name={self.name}, "
            f"code={self.code})>"
        )