from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.hospital_group_repository import HospitalGroupRepository
from app.repositories.branch_kpi_repository import BranchKPIRepository


class DashboardSummaryService:

    def __init__(self, db: AsyncSession):
        self.db = db

        self.analytics_repository = AnalyticsRepository(db)
        self.report_repository = ReportRepository(db)
        self.group_repository = HospitalGroupRepository(db)
        self.kpi_repository = BranchKPIRepository(db)

    # Corporate Dashboard Summary
    async def dashboard_summary(
        self,
        corporate_account_id: UUID,
    ):

        summary = await self.analytics_repository.get_dashboard_summary(
            corporate_account_id
        )

        monthly_revenue = (
            await self.analytics_repository.get_monthly_revenue(
                corporate_account_id
            )
        )

        top_hospitals = (
            await self.analytics_repository.get_top_hospitals(
                corporate_account_id,
                limit=5,
            )
        )

        reports = (
            await self.report_repository.get_recent_reports(
                corporate_account_id,
                limit=5,
            )
        )

        report_statistics = (
            await self.report_repository.get_statistics(
                corporate_account_id
            )
        )

        total_groups = (
            await self.group_repository.count(
                corporate_account_id
            )
        )

        total_kpis = (
            await self.kpi_repository.count(
                corporate_account_id
            )
        )

        cards = {
            "hospital_groups": total_groups,
            "kpis": total_kpis,
            "hospitals": summary.hospitals,
            "doctors": summary[2],
            "staff": summary[3],
            "patients": summary[4],
            "revenue": summary[5],
            "expenses": summary[6],
            "profit": summary[7],
        }

        charts = {
            "monthly_revenue": monthly_revenue,
        }

        return {
            "cards": cards,
            "charts": charts,
            "top_hospitals": top_hospitals,
            "recent_reports": reports,
            "report_statistics": {
                "total_reports": report_statistics.total_reports,
                "completed_reports": report_statistics.completed_reports,
                "pending_reports": report_statistics.pending_reports,
                "failed_reports": report_statistics.failed_reports,
                "downloaded_reports": report_statistics.downloaded_reports,
                "total_downloads": report_statistics.total_downloads,
            },
        }

    # Overview Cards
    async def overview_cards(
        self,
        corporate_account_id: UUID,
    ):

        return {
            "total_groups": await self.group_repository.count(
                corporate_account_id
            ),
            "total_kpis": await self.kpi_repository.count(
                corporate_account_id
            ),
            "total_revenue": await self.kpi_repository.total_revenue(
                corporate_account_id
            ),
            "total_profit": await self.kpi_repository.total_profit(
                corporate_account_id
            ),
            "total_patients": await self.kpi_repository.total_patients(
                corporate_account_id
            ),
            "total_doctors": await self.kpi_repository.total_doctors(
                corporate_account_id
            ),
        }

    # Revenue Dashboard
    async def revenue_dashboard(
        self,
        corporate_account_id: UUID,
    ):

        return {
            "monthly_revenue": await self.analytics_repository.get_monthly_revenue(
                corporate_account_id
            ),
            "top_hospitals": await self.analytics_repository.get_top_hospitals(
                corporate_account_id
            ),
            "total_revenue": await self.kpi_repository.total_revenue(
                corporate_account_id
            ),
            "total_profit": await self.kpi_repository.total_profit(
                corporate_account_id
            ),
        }

    # KPI Dashboard
    async def kpi_dashboard(
        self,
        corporate_account_id: UUID,
    ):

        return await self.kpi_repository.get_corporate_kpis(
            corporate_account_id,
            skip=0,
            limit=100,
        )