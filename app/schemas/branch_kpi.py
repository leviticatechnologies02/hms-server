from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# Create
class BranchKPICreate(BaseModel):

    corporate_account_id: UUID
    hospital_group_id: UUID
    hospital_id: UUID

    report_date: date

    month: int
    year: int

    total_patients: int = 0
    new_patients: int = 0
    returning_patients: int = 0
    admitted_patients: int = 0
    discharged_patients: int = 0
    emergency_cases: int = 0

    total_appointments: int = 0
    completed_appointments: int = 0
    cancelled_appointments: int = 0
    missed_appointments: int = 0

    total_revenue: Decimal = Decimal("0")
    total_expenses: Decimal = Decimal("0")
    net_profit: Decimal = Decimal("0")
    outstanding_amount: Decimal = Decimal("0")

    total_doctors: int = 0
    total_nurses: int = 0
    total_staff: int = 0
    active_staff: int = 0

    bed_occupancy_percentage: Decimal = Decimal("0")
    average_waiting_time: int = 0
    patient_satisfaction: Decimal = Decimal("0")
    average_consultation_time: int = 0

    remarks: Optional[str] = None

# Update
class BranchKPIUpdate(BaseModel):

    total_patients: Optional[int] = None
    new_patients: Optional[int] = None
    returning_patients: Optional[int] = None
    admitted_patients: Optional[int] = None
    discharged_patients: Optional[int] = None
    emergency_cases: Optional[int] = None

    total_appointments: Optional[int] = None
    completed_appointments: Optional[int] = None
    cancelled_appointments: Optional[int] = None
    missed_appointments: Optional[int] = None

    total_revenue: Optional[Decimal] = None
    total_expenses: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    outstanding_amount: Optional[Decimal] = None

    total_doctors: Optional[int] = None
    total_nurses: Optional[int] = None
    total_staff: Optional[int] = None
    active_staff: Optional[int] = None

    bed_occupancy_percentage: Optional[Decimal] = None
    average_waiting_time: Optional[int] = None
    patient_satisfaction: Optional[Decimal] = None
    average_consultation_time: Optional[int] = None

    remarks: Optional[str] = None

    is_active: Optional[bool] = None

# Response
class BranchKPIResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    corporate_account_id: UUID
    hospital_group_id: UUID
    hospital_id: UUID

    report_date: date

    month: int
    year: int

    total_patients: int
    new_patients: int
    returning_patients: int
    admitted_patients: int
    discharged_patients: int
    emergency_cases: int

    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    missed_appointments: int

    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    outstanding_amount: Decimal

    total_doctors: int
    total_nurses: int
    total_staff: int
    active_staff: int

    bed_occupancy_percentage: Decimal
    average_waiting_time: int
    patient_satisfaction: Decimal
    average_consultation_time: int

    profit_margin: float

    remarks: Optional[str]

    is_active: bool

    created_at: datetime
    updated_at: datetime