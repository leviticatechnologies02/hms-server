from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branch_kpi import BranchKPI
from app.models.hospital_group import HospitalGroup
from app.models.hospital import Hospital


class AnalyticsRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Dashboard
    async def get_dashboard_summary(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.count(func.distinct(HospitalGroup.id)).label("groups"),
                func.count(func.distinct(Hospital.id)).label("hospitals"),
                func.coalesce(func.sum(BranchKPI.total_doctors), 0),
                func.coalesce(func.sum(BranchKPI.total_staff), 0),
                func.coalesce(func.sum(BranchKPI.total_patients), 0),
                func.coalesce(func.sum(BranchKPI.total_revenue), 0),
                func.coalesce(func.sum(BranchKPI.total_expenses), 0),
                func.coalesce(func.sum(BranchKPI.net_profit), 0),
            )
            .select_from(BranchKPI)
            .join(
                HospitalGroup,
                BranchKPI.hospital_group_id == HospitalGroup.id,
            )
            .join(
                Hospital,
                BranchKPI.hospital_id == Hospital.id,
            )
            .where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.one()

    # Revenue
    async def get_total_revenue(
        self,
        corporate_account_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ):

        query = select(
            func.coalesce(func.sum(BranchKPI.total_revenue), 0)
        ).where(
            BranchKPI.corporate_account_id == corporate_account_id,
            BranchKPI.is_active == True,
        )

        if from_date:
            query = query.where(BranchKPI.report_date >= from_date)

        if to_date:
            query = query.where(BranchKPI.report_date <= to_date)

        result = await self.db.execute(query)

        return result.scalar()

    # Expenses
    async def get_total_expenses(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(BranchKPI.total_expenses),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Profit
    async def get_total_profit(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(BranchKPI.net_profit),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Patient Count
    async def get_total_patients(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.coalesce(
                    func.sum(BranchKPI.total_patients),
                    0,
                )
            ).where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
        )

        return result.scalar()

    # Top Hospitals
    async def get_top_hospitals(
        self,
        corporate_account_id: UUID,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(
                Hospital.name,
                func.sum(
                    BranchKPI.total_revenue
                ).label("revenue"),
                func.sum(
                    BranchKPI.total_patients
                ).label("patients"),
                func.avg(
                    BranchKPI.patient_satisfaction
                ).label("satisfaction"),
            )
            .join(
                Hospital,
                BranchKPI.hospital_id == Hospital.id,
            )
            .where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
            .group_by(Hospital.id)
            .order_by(
                func.sum(
                    BranchKPI.total_revenue
                ).desc()
            )
            .limit(limit)
        )

        return result.all()

    # Monthly Revenue
    async def get_monthly_revenue(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                BranchKPI.year,
                BranchKPI.month,
                func.sum(
                    BranchKPI.total_revenue
                ).label("revenue"),
            )
            .where(
                BranchKPI.corporate_account_id == corporate_account_id,
                BranchKPI.is_active == True,
            )
            .group_by(
                BranchKPI.year,
                BranchKPI.month,
            )
            .order_by(
                BranchKPI.year,
                BranchKPI.month,
            )
        )

        return result.all()

    # KPI List
    async def get_branch_kpis(
        self,
        corporate_account_id: UUID,
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
        )

        return result.scalars().all()