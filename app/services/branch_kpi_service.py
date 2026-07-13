from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branch_kpi import BranchKPI
from app.repositories.branch_kpi_repository import (
    BranchKPIRepository,
)


class BranchKPIService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BranchKPIRepository(db)

    # Create KPI
    async def create(
        self,
        payload,
    ):

        kpi = BranchKPI(
            **payload.model_dump()
        )

        return await self.repository.create(
            kpi
        )

    # Get KPI
    async def get(
        self,
        kpi_id: UUID,
    ):

        kpi = await self.repository.get_by_id(
            kpi_id
        )

        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch KPI not found.",
            )

        return kpi

    # Corporate KPI List
    async def corporate_kpis(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        return await self.repository.get_corporate_kpis(
            corporate_account_id,
            skip,
            limit,
        )

    # Hospital KPI
    async def hospital_kpis(
        self,
        hospital_id: UUID,
    ):

        return await self.repository.get_hospital_kpi(
            hospital_id
        )

    # Group KPI
    async def group_kpis(
        self,
        group_id: UUID,
    ):

        return await self.repository.get_group_kpis(
            group_id
        )

    # KPI By Date Range
    async def between_dates(
        self,
        corporate_account_id: UUID,
        from_date,
        to_date,
    ):

        return await self.repository.get_between_dates(
            corporate_account_id,
            from_date,
            to_date,
        )

    # Update KPI
    async def update(
        self,
        kpi_id: UUID,
        payload,
    ):

        kpi = await self.repository.get_by_id(
            kpi_id
        )

        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch KPI not found.",
            )

        values = payload.model_dump(
            exclude_unset=True
        )

        for key, value in values.items():
            setattr(kpi, key, value)

        return await self.repository.update(
            kpi
        )

    # Delete KPI
    async def delete(
        self,
        kpi_id: UUID,
    ):

        kpi = await self.repository.get_by_id(
            kpi_id
        )

        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch KPI not found.",
            )

        await self.repository.delete(
            kpi
        )

        return {
            "message": "Branch KPI deleted successfully."
        }

    # Dashboard Summary
    async def dashboard_summary(
        self,
        corporate_account_id: UUID,
    ):

        return {
            "total_kpis": await self.repository.count(
                corporate_account_id
            ),
            "total_revenue": await self.repository.total_revenue(
                corporate_account_id
            ),
            "total_profit": await self.repository.total_profit(
                corporate_account_id
            ),
            "total_patients": await self.repository.total_patients(
                corporate_account_id
            ),
            "total_doctors": await self.repository.total_doctors(
                corporate_account_id
            ),
        }