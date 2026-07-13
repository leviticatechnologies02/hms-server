from uuid import UUID
from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.schemas.branch_kpi import (
    BranchKPICreate,
    BranchKPIUpdate,
    BranchKPIResponse,
)

from app.services.branch_kpi_service import BranchKPIService

router = APIRouter(
    prefix="/corporate/kpis",
    tags=["Corporate Branch KPI"],
)

# Create KPI
@router.post(
    "",
    response_model=BranchKPIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_kpi(
    payload: BranchKPICreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)
    return await service.create(payload)

# Get KPI
@router.get(
    "/{kpi_id}",
    response_model=BranchKPIResponse,
)
async def get_kpi(
    kpi_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)
    return await service.get(kpi_id)

# Corporate KPI List
@router.get("")
async def corporate_kpis(
    corporate_account_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.corporate_kpis(
        corporate_account_id,
        skip,
        limit,
    )

# Hospital KPI
@router.get("/hospital/{hospital_id}")
async def hospital_kpis(
    hospital_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.hospital_kpis(
        hospital_id
    )

# Group KPI
@router.get("/group/{group_id}")
async def group_kpis(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.group_kpis(
        group_id
    )

# KPI Between Dates
@router.get("/date-range")
async def date_range(
    corporate_account_id: UUID,
    from_date: date,
    to_date: date,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.between_dates(
        corporate_account_id,
        from_date,
        to_date,
    )

# Update KPI
@router.put(
    "/{kpi_id}",
    response_model=BranchKPIResponse,
)
async def update_kpi(
    kpi_id: UUID,
    payload: BranchKPIUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.update(
        kpi_id,
        payload,
    )

# Delete KPI
@router.delete("/{kpi_id}")
async def delete_kpi(
    kpi_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.delete(
        kpi_id
    )

# Dashboard Summary
@router.get("/dashboard/summary")
async def dashboard_summary(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = BranchKPIService(db)

    return await service.dashboard_summary(
        corporate_account_id
    )