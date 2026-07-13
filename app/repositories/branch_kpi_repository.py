from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branch_kpi import BranchKPI


class BranchKPIRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        kpi: BranchKPI,
    ) -> BranchKPI:

        self.db.add(kpi)
        await self.db.commit()
        await self.db.refresh(kpi)

        return kpi

    # Get By ID
    async def get_by_id(
        self,
        kpi_id: UUID,
    ) -> Optional[BranchKPI]:

        result = await self.db.execute(
            select(BranchKPI).where(
                BranchKPI.id == kpi_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # Get Hospital KPI
    async def get_hospital_kpi(
        self,
        hospital_id: UUID,
    ):

        result = await self.db.execute(
            select(BranchKPI)
            .where(
                BranchKPI.hospital_id == hospital_id,
                BranchKPI.is_active == True,
            )
            .order_by(
                BranchKPI.report_date.desc()
            )
        )

        return result.scalars().all()

    # Corporate KPIs
    async def get_corporate_kpis(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        result = await self.db.execute(
            select(BranchKPI)
            .where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
            .order_by(
                BranchKPI.report_date.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    # Group KPIs
    async def get_group_kpis(
        self,
        group_id: UUID,
    ):

        result = await self.db.execute(
            select(BranchKPI)
            .where(
                BranchKPI.hospital_group_id == group_id,
                BranchKPI.is_active == True,
            )
            .order_by(
                BranchKPI.report_date.desc()
            )
        )

        return result.scalars().all()

    # Date Range
    async def get_between_dates(
        self,
        corporate_account_id: UUID,
        from_date: date,
        to_date: date,
    ):

        result = await self.db.execute(
            select(BranchKPI)
            .where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.report_date >= from_date,
                BranchKPI.report_date <= to_date,
                BranchKPI.is_active == True,
            )
            .order_by(
                BranchKPI.report_date.desc()
            )
        )

        return result.scalars().all()

    # Update
    async def update(
        self,
        kpi: BranchKPI,
    ) -> BranchKPI:

        await self.db.commit()
        await self.db.refresh(kpi)

        return kpi

    # Delete
    async def delete(
        self,
        kpi: BranchKPI,
    ):

        kpi.is_active = False

        await self.db.commit()

    # Count
    async def count(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.count(
                    BranchKPI.id
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Revenue
    async def total_revenue(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        BranchKPI.total_revenue
                    ),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Profit
    async def total_profit(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        BranchKPI.net_profit
                    ),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Patients
    async def total_patients(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        BranchKPI.total_patients
                    ),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Doctors
    async def total_doctors(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(
                        BranchKPI.total_doctors
                    ),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()