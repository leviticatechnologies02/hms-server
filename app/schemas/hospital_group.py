from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Create
class HospitalGroupCreate(BaseModel):
    corporate_account_id: UUID

    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=50)

    description: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

# Update
class HospitalGroupUpdate(BaseModel):
    name: Optional[str] = None

    description: Optional[str] = None

    email: Optional[str] = None
    phone: Optional[str] = None

    address: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    is_active: Optional[bool] = None

# Response
class HospitalGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    corporate_account_id: UUID

    name: str
    code: str
    description: Optional[str]

    email: Optional[str]
    phone: Optional[str]

    address: Optional[str]

    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]

    total_hospitals: int
    total_branches: int

    total_doctors: int
    total_staff: int
    total_patients: int

    total_members: int

    is_active: bool
    is_deleted: bool

    created_at: datetime
    updated_at: datetime

# List Response
class HospitalGroupListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str
    code: str

    city: Optional[str]
    state: Optional[str]

    total_hospitals: int
    total_branches: int

    total_doctors: int
    total_staff: int
    total_patients: int

    is_active: bool

# Hospital Mapping
class AssignHospitalGroup(BaseModel):
    hospital_id: UUID

class RemoveHospitalGroup(BaseModel):
    hospital_id: UUID