from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict

# Dashboard Cards
class DashboardCard(BaseModel):
    title: str
    value: Decimal | int | float
    change_percentage: float
    trend: str  # up | down | stable

# Revenue Chart
class RevenueChartItem(BaseModel):
    month: str
    revenue: Decimal

# Patient Chart
class PatientChartItem(BaseModel):
    month: str
    patients: int

# Hospital Performance
class HospitalPerformanceItem(BaseModel):
    hospital_id: str
    hospital_name: str

    revenue: Decimal
    patients: int
    appointments: int

    bed_occupancy: float
    patient_satisfaction: float

# KPI
class KPIResponse(BaseModel):
    total_patients: int
    new_patients: int

    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int

    total_doctors: int
    total_staff: int

    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal

    outstanding_amount: Decimal

    average_waiting_time: float
    average_consultation_time: float

    bed_occupancy_percentage: float
    patient_satisfaction: float

# Dashboard Response
class CorporateDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    corporate_name: str

    total_groups: int
    total_hospitals: int
    total_branches: int

    total_doctors: int
    total_staff: int

    total_patients: int

    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal

    cards: List[DashboardCard]

    revenue_chart: List[RevenueChartItem]

    patient_chart: List[PatientChartItem]

    top_hospitals: List[HospitalPerformanceItem]

# Dashboard Filter
class DashboardFilter(BaseModel):
    from_date: date
    to_date: date

# KPI Filter
class KPIFilter(BaseModel):
    from_date: date
    to_date: date

    hospital_id: str | None = None
    group_id: str | None = None