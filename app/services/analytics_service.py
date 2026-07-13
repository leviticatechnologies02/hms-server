from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import AnalyticsRepository

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AnalyticsRepository(db)

    # Corporate Dashboard
    async def get_dashboard(
        self,
        corporate_account_id: UUID,
    ):

        summary = await self.repository.get_dashboard_summary(
            corporate_account_id
        )
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate analytics not found.",
            )
        monthly_revenue = await self.repository.get_monthly_revenue(
            corporate_account_id
        )
        top_hospitals = await self.repository.get_top_hospitals(
            corporate_account_id
        )
        return {
            "summary": summary,
            "monthly_revenue": monthly_revenue,
            "top_hospitals": top_hospitals,
        }

    # KPI Dashboard
    async def get_kpis(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_branch_kpis(
            corporate_account_id
        )
    # Revenue
    async def get_total_revenue(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_total_revenue(
            corporate_account_id
        )
    # Expenses
    async def get_total_expenses(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_total_expenses(
            corporate_account_id
        )

    # Profit
    async def get_total_profit(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_total_profit(
            corporate_account_id
        )

    # Patients
    async def get_total_patients(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_total_patients(
            corporate_account_id
        )

    # Monthly Revenue
    async def get_monthly_revenue(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_monthly_revenue(
            corporate_account_id
        )

    # Top Hospitals
    async def get_top_hospitals(
        self,
        corporate_account_id: UUID,
    ):
        return await self.repository.get_top_hospitals(
            corporate_account_id
        )

    # Dashboard Cards
    async def dashboard_cards(
        self,
        corporate_account_id: UUID,
    ):
        revenue = await self.repository.get_total_revenue(
            corporate_account_id
        )
        expenses = await self.repository.get_total_expenses(
            corporate_account_id
        )
        profit = await self.repository.get_total_profit(
            corporate_account_id
        )

        patients = await self.repository.get_total_patients(
            corporate_account_id
        )

        return {
            "total_revenue": revenue,
            "total_expenses": expenses,
            "net_profit": profit,
            "total_patients": patients,
        }