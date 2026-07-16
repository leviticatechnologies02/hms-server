from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....schemas.common import ResponseModel
from ....schemas.hospital import (
    HospitalCreate,
    HospitalUpdate,
)
from ....services.hospital import HospitalService

router = APIRouter(
    prefix="/hospitals",
    tags=["Super Admin - Hospitals"],
)


@router.post(
    "/",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_hospital(
    data: HospitalCreate,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    hospital = await service.create_hospital(
        data,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Hospital created successfully",
        data=hospital.model_dump(),
    )


@router.get(
    "/",
    response_model=ResponseModel,
)
async def list_hospitals(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    skip = (page - 1) * limit

    hospitals, total = await service.get_hospitals(
        skip=skip,
        limit=limit,
        search=search,
    )

    return ResponseModel(
        success=True,
        message="Hospitals retrieved successfully",
        data={
            "items": [
                hospital.model_dump()
                for hospital in hospitals
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (
                (total + limit - 1) // limit
                if total
                else 0
            ),
        },
    )


@router.get(
    "/{hospital_id}",
    response_model=ResponseModel,
)
async def get_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    hospital = await service.get_hospital(
        hospital_id,
    )

    return ResponseModel(
        success=True,
        message="Hospital retrieved successfully",
        data=hospital.model_dump(),
    )


@router.put(
    "/{hospital_id}",
    response_model=ResponseModel,
)
async def update_hospital(
    hospital_id: UUID,
    data: HospitalUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    hospital = await service.update_hospital(
        hospital_id,
        data,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Hospital updated successfully",
        data=hospital.model_dump(),
    )


@router.delete(
    "/{hospital_id}",
    response_model=ResponseModel,
)
async def deactivate_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    await service.deactivate_hospital(
        hospital_id,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Hospital deactivated successfully",
        data=None,
    )


@router.post(
    "/{hospital_id}/activate",
    response_model=ResponseModel,
)
async def activate_hospital(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    hospital = await service.activate_hospital(
        hospital_id,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Hospital activated successfully",
        data=hospital.model_dump(),
    )


@router.get(
    "/{hospital_id}/subscription",
    response_model=ResponseModel,
)
async def get_hospital_subscription(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = HospitalService(db)

    result = await service.get_hospital_with_subscription(
        hospital_id,
    )

    if not result:
        return ResponseModel(
            success=False,
            message="Hospital not found",
            data=None,
        )

    return ResponseModel(
        success=True,
        message="Hospital subscription retrieved successfully",
        data=result,
    )