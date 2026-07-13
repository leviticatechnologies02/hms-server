from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from ....core.database import get_db
from ....core.dependencies import get_current_super_admin, require_permission
from ....models.user import User
from ....schemas.hospital import (
    HospitalCreate, HospitalUpdate, HospitalResponse, HospitalListResponse
)
from ....schemas.common import ResponseModel, PaginationParams
from ....services.hospital import HospitalService
from ....services.audit import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hospitals", tags=["Super Admin - Hospitals"])


@router.post(
    "/",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create Hospital",
    description="Create a new hospital in the platform"
)
async def create_hospital(
    data: HospitalCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new hospital."""
    service = HospitalService(db)
    hospital = service.create_hospital(data, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Hospital created successfully",
        data=hospital.model_dump()
    )


@router.get(
    "/",
    response_model=ResponseModel,
    summary="List Hospitals",
    description="Get list of all hospitals with pagination"
)
async def list_hospitals(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, code, or email"),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """List all hospitals."""
    service = HospitalService(db)
    skip = (page - 1) * limit
    hospitals, total = service.get_hospitals(skip, limit, search)
    
    return ResponseModel(
        success=True,
        message="Hospitals retrieved successfully",
        data={
            "items": [h.model_dump() for h in hospitals],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    )


@router.get(
    "/{hospital_id}",
    response_model=ResponseModel,
    summary="Get Hospital",
    description="Get hospital details by ID"
)
async def get_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get hospital by ID."""
    service = HospitalService(db)
    hospital = service.get_hospital(hospital_id)
    
    return ResponseModel(
        success=True,
        message="Hospital retrieved successfully",
        data=hospital.model_dump()
    )


@router.put(
    "/{hospital_id}",
    response_model=ResponseModel,
    summary="Update Hospital",
    description="Update hospital details"
)
async def update_hospital(
    hospital_id: UUID,
    data: HospitalUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Update hospital."""
    service = HospitalService(db)
    hospital = service.update_hospital(hospital_id, data, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Hospital updated successfully",
        data=hospital.model_dump()
    )


@router.delete(
    "/{hospital_id}",
    response_model=ResponseModel,
    summary="Deactivate Hospital",
    description="Soft delete/deactivate a hospital"
)
async def deactivate_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Deactivate hospital."""
    service = HospitalService(db)
    service.deactivate_hospital(hospital_id, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Hospital deactivated successfully",
        data=None
    )


@router.post(
    "/{hospital_id}/activate",
    response_model=ResponseModel,
    summary="Activate Hospital",
    description="Activate a deactivated hospital"
)
async def activate_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Activate hospital."""
    service = HospitalService(db)
    hospital = service.activate_hospital(hospital_id, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Hospital activated successfully",
        data=hospital.model_dump()
    )


@router.get(
    "/{hospital_id}/subscription",
    response_model=ResponseModel,
    summary="Get Hospital Subscription",
    description="Get subscription details for a hospital"
)
async def get_hospital_subscription(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get hospital with subscription details."""
    service = HospitalService(db)
    result = service.get_hospital_with_subscription(hospital_id)
    
    if not result:
        return ResponseModel(
            success=False,
            message="Hospital not found",
            data=None
        )
    
    return ResponseModel(
        success=True,
        message="Hospital subscription retrieved successfully",
        data=result
    )