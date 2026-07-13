from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.hospital_group import (
    HospitalGroupCreate,
    HospitalGroupUpdate,
    HospitalGroupResponse,
    AssignHospitalGroup,
)

from app.services.hospital_group_service import HospitalGroupService

router = APIRouter(
    prefix="/corporate/groups",
    tags=["Corporate Hospital Groups"],
)

# Create Hospital Group
@router.post(
    "",
    response_model=HospitalGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group(
    payload: HospitalGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)
    return await service.create(payload)

# List Hospital Groups
@router.get("")
async def list_groups(
    corporate_account_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.list(
        corporate_account_id,
        skip,
        limit,
    )

# Get Group
@router.get(
    "/{group_id}",
    response_model=HospitalGroupResponse,
)
async def get_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)
    return await service.get(group_id)

# Update Group
@router.put(
    "/{group_id}",
    response_model=HospitalGroupResponse,
)
async def update_group(
    group_id: UUID,
    payload: HospitalGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.update(
        group_id,
        payload,
    )

# Delete Group
@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)
    return await service.delete(group_id)

# Activate Group
@router.patch("/{group_id}/activate")
async def activate_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)
    return await service.activate(group_id)

# Deactivate Group
@router.patch("/{group_id}/deactivate")
async def deactivate_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)
    return await service.deactivate(group_id)

# Assign Hospital
@router.post("/{group_id}/assign-hospital")
async def assign_hospital(
    group_id: UUID,
    payload: AssignHospitalGroup,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.assign_hospital(
        group_id,
        payload.hospital_id,
    )


# Remove Hospital
@router.delete("/{group_id}/remove-hospital/{hospital_id}")
async def remove_hospital(
    group_id: UUID,
    hospital_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.remove_hospital(
        group_id,
        hospital_id,
    )

# Group Hospitals
@router.get("/{group_id}/hospitals")
async def group_hospitals(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.hospitals(group_id)

# Search Groups
@router.get("/search")
async def search_groups(
    corporate_account_id: UUID,
    keyword: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return await service.search(
        corporate_account_id,
        keyword,
    )

# Count Groups
@router.get("/statistics/count")
async def total_groups(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = HospitalGroupService(db)

    return {
        "total_groups": await service.count(
            corporate_account_id
        )
    }