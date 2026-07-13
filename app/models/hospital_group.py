from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Text,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditMixin

class HospitalGroup(BaseModel, AuditMixin):
    """
    Corporate Hospital Group

    One Corporate Account
        └── Multiple Hospital Groups
                └── Multiple Hospitals
    """

    __tablename__ = "hospital_groups"

    # Corporate
    corporate_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("corporate_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Details
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Statistics
    total_hospitals = Column(Integer, default=0)
    total_branches = Column(Integer, default=0)
    total_doctors = Column(Integer, default=0)
    total_staff = Column(Integer, default=0)
    total_patients = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    corporate_account = relationship(
        "CorporateAccount",
        back_populates="hospital_groups",
    )

    hospitals = relationship(
        "Hospital",
        back_populates="hospital_group",
        cascade="all, delete-orphan",
    )

    branch_kpis = relationship(
        "BranchKPI",
        back_populates="hospital_group",
        cascade="all, delete-orphan",
    )

    # Helpers
    @property
    def total_members(self):
        return self.total_doctors + self.total_staff

    def __repr__(self):
        return (
            f"<HospitalGroup("
            f"name={self.name}, "
            f"code={self.code})>"
        )