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

from app.schemas.corporate import (
    CorporateCreate,
    CorporateUpdate,
    CorporateResponse,
)

from app.schemas.report import (
    ReportGenerateRequest,
)

from app.services.corporate_service import CorporateService
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService

router = APIRouter(prefix="/corporate", tags=["Corporate Admin"])

# Corporate CRUD
@router.post(
    "",
    response_model=CorporateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_corporate(
    payload: CorporateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.create(payload)


@router.get(
    "",
)
async def list_corporates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.get_all(skip, limit)


@router.get(
    "/{corporate_id}",
    response_model=CorporateResponse,
)
async def get_corporate(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.get_by_id(corporate_id)


@router.put(
    "/{corporate_id}",
    response_model=CorporateResponse,
)
async def update_corporate(
    corporate_id: UUID,
    payload: CorporateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.update(
        corporate_id,
        payload,
    )


@router.delete(
    "/{corporate_id}",
)
async def delete_corporate(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.delete(corporate_id)


@router.patch(
    "/{corporate_id}/activate",
)
async def activate_corporate(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.activate(corporate_id)


@router.patch(
    "/{corporate_id}/deactivate",
)
async def deactivate_corporate(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CorporateService(db)
    return await service.deactivate(corporate_id)

# Dashboard
@router.get(
    "/{corporate_id}/dashboard",
)
async def corporate_dashboard(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_dashboard(corporate_id)


@router.get(
    "/{corporate_id}/dashboard/cards",
)
async def dashboard_cards(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.dashboard_cards(corporate_id)


@router.get(
    "/{corporate_id}/kpis",
)
async def get_kpis(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_kpis(corporate_id)


@router.get(
    "/{corporate_id}/top-hospitals",
)
async def top_hospitals(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_top_hospitals(corporate_id)


@router.get(
    "/{corporate_id}/monthly-revenue",
)
async def monthly_revenue(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AnalyticsService(db)
    return await service.get_monthly_revenue(corporate_id)

# Reports
@router.post(
    "/reports",
)
async def generate_report(
    payload: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.generate_report(
        payload,
        current_user.id,
    )


@router.get(
    "/{corporate_id}/reports",
)
async def list_reports(
    corporate_id: UUID,
    skip: int = Query(0),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.get_reports(
        corporate_id,
        skip,
        limit,
    )


@router.get(
    "/reports/{report_id}",
)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.get_report(report_id)


@router.get(
    "/reports/{report_id}/download",
)
async def download_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.download_report(report_id)


@router.delete(
    "/reports/{report_id}",
)
async def delete_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.delete_report(report_id)


@router.get(
    "/{corporate_id}/report-statistics",
)
async def report_statistics(
    corporate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.statistics(corporate_id)


@router.get(
    "/{corporate_id}/recent-reports",
)
async def recent_reports(
    corporate_id: UUID,
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReportService(db)
    return await service.recent_reports(
        corporate_id,
        limit,
    )