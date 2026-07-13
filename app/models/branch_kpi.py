from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    Date,
    Boolean,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditMixin

class BranchKPI(BaseModel, AuditMixin):
    """
    Branch KPI Model

    Stores analytics and performance metrics
    for each hospital/branch.
    """

    __tablename__ = "branch_kpis"
    # Relationships
    corporate_account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("corporate_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hospital_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hospital_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hospital_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # KPI Period
    report_date = Column(Date, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Patient Statistics
    total_patients = Column(Integer, default=0)
    new_patients = Column(Integer, default=0)
    returning_patients = Column(Integer, default=0)
    admitted_patients = Column(Integer, default=0)
    discharged_patients = Column(Integer, default=0)
    emergency_cases = Column(Integer, default=0)

    # Appointment Statistics
    total_appointments = Column(Integer, default=0)
    completed_appointments = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
    missed_appointments = Column(Integer, default=0)

    # Financial KPIs
    total_revenue = Column(
        Numeric(15, 2),
        default=0,
    )
    total_expenses = Column(
        Numeric(15, 2),
        default=0,
    )
    net_profit = Column(
        Numeric(15, 2),
        default=0,
    )
    outstanding_amount = Column(
        Numeric(15, 2),
        default=0,
    )

    # Staff KPIs
    total_doctors = Column(Integer, default=0)
    total_nurses = Column(Integer, default=0)
    total_staff = Column(Integer, default=0)
    active_staff = Column(Integer, default=0)

    # Operational KPIs
    bed_occupancy_percentage = Column(
        Numeric(5, 2),
        default=0,
    )
    average_waiting_time = Column(Integer, default=0)
    patient_satisfaction = Column(
        Numeric(5, 2),
        default=0,
    )
    average_consultation_time = Column(Integer, default=0)

    # Remarks
    remarks = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    corporate_account = relationship(
        "CorporateAccount",
    )

    hospital_group = relationship(
        "HospitalGroup",
        back_populates="branch_kpis",
    )

    hospital = relationship(
        "Hospital",
    )

    # Helpers
    @property
    def profit_margin(self):
        if float(self.total_revenue) == 0:
            return 0

        return round(
            (float(self.net_profit) / float(self.total_revenue)) * 100,
            2,
        )

    def __repr__(self):
        return (
            f"<BranchKPI("
            f"hospital={self.hospital_id}, "
            f"month={self.month}, "
            f"year={self.year})>"
        )