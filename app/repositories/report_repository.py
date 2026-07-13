from typing import Optional
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.corporate_report import CorporateReport


class ReportRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        report: CorporateReport,
    ) -> CorporateReport:

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        return report

    # Get By ID
    async def get_by_id(
        self,
        report_id: UUID,
    ) -> Optional[CorporateReport]:

        result = await self.db.execute(
            select(CorporateReport).where(
                CorporateReport.id == report_id,
                CorporateReport.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # Get By Code
    async def get_by_code(
        self,
        report_code: str,
    ) -> Optional[CorporateReport]:

        result = await self.db.execute(
            select(CorporateReport).where(
                CorporateReport.report_code == report_code,
                CorporateReport.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # Get All
    async def get_all(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        result = await self.db.execute(
            select(CorporateReport)
            .where(
                CorporateReport.corporate_account_id == corporate_account_id,
                CorporateReport.is_active == True,
            )
            .order_by(CorporateReport.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    # Count
    async def count(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(func.count(CorporateReport.id)).where(
                CorporateReport.corporate_account_id == corporate_account_id,
                CorporateReport.is_active == True,
            )
        )

        return result.scalar()

    # Update
    async def update(
        self,
        report: CorporateReport,
    ) -> CorporateReport:

        await self.db.commit()
        await self.db.refresh(report)

        return report

    # Delete
    async def delete(
        self,
        report: CorporateReport,
    ):

        report.is_active = False

        await self.db.commit()

    # Reports By Status
    async def get_by_status(
        self,
        corporate_account_id: UUID,
        status: str,
    ):

        result = await self.db.execute(
            select(CorporateReport)
            .where(
                CorporateReport.corporate_account_id == corporate_account_id,
                CorporateReport.status == status,
                CorporateReport.is_active == True,
            )
            .order_by(CorporateReport.created_at.desc())
        )

        return result.scalars().all()

    # Download
    async def mark_downloaded(
        self,
        report: CorporateReport,
    ):

        report.is_downloaded = True
        report.download_count += 1

        await self.db.commit()
        await self.db.refresh(report)

        return report

    # Dashboard Statistics
    async def get_statistics(
        self,
        corporate_account_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.count(CorporateReport.id).label("total_reports"),
                func.count().filter(
                    CorporateReport.status == "COMPLETED"
                ).label("completed_reports"),
                func.count().filter(
                    CorporateReport.status == "PENDING"
                ).label("pending_reports"),
                func.count().filter(
                    CorporateReport.status == "FAILED"
                ).label("failed_reports"),
                func.count().filter(
                    CorporateReport.is_downloaded == True
                ).label("downloaded_reports"),
                func.coalesce(
                    func.sum(CorporateReport.download_count),
                    0,
                ).label("total_downloads"),
            )
            .where(
                CorporateReport.corporate_account_id == corporate_account_id,
                CorporateReport.is_active == True,
            )
        )

        return result.one()
    # Recent Reports
    async def get_recent_reports(
        self,
        corporate_account_id: UUID,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(CorporateReport)
            .where(
                CorporateReport.corporate_account_id == corporate_account_id,
                CorporateReport.is_active == True,
            )
            .order_by(CorporateReport.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()