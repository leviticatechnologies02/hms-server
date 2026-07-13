from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Create
class CorporateCreate(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)

    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    tax_number: Optional[str] = None

    description: Optional[str] = None

    email: EmailStr
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None

    website: Optional[str] = None
    logo: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    max_hospitals: int = 1
    max_branches: int = 1
    max_users: int = 100
    max_storage_gb: int = 100

# Update
class CorporateUpdate(BaseModel):
    name: Optional[str] = None
    legal_name: Optional[str] = None

    registration_number: Optional[str] = None
    tax_number: Optional[str] = None

    description: Optional[str] = None

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    alternate_phone: Optional[str] = None

    website: Optional[str] = None
    logo: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    max_hospitals: Optional[int] = None
    max_branches: Optional[int] = None
    max_users: Optional[int] = None
    max_storage_gb: Optional[int] = None

    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

# Response
class CorporateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    code: str
    legal_name: Optional[str]
    registration_number: Optional[str]
    tax_number: Optional[str]
    description: Optional[str]
    email: EmailStr
    phone: Optional[str]
    alternate_phone: Optional[str]
    website: Optional[str]
    logo: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    max_hospitals: int
    max_branches: int
    max_users: int
    max_storage_gb: int
    current_storage_gb: Decimal
    available_storage: float
    storage_usage_percentage: float
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

# Dashboard
class DashboardResponse(BaseModel):
    total_hospital_groups: int
    total_hospitals: int
    total_branches: int

    total_doctors: int
    total_staff: int
    total_patients: int

    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal

    average_bed_occupancy: float
    average_patient_satisfaction: float

    monthly_growth: float