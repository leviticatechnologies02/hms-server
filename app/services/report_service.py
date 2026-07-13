import uuid
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.corporate_report import CorporateReport
from app.repositories.report_repository import ReportRepository
from app.schemas.report import (
    ReportGenerateRequest,
    ReportUpdate,
)

class ReportService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReportRepository(db)

    # Generate Report
    async def generate_report(
        self,
        payload: ReportGenerateRequest,
        generated_by: UUID,
    ):

        report = CorporateReport(
            corporate_account_id=payload.corporate_account_id,
            generated_by=generated_by,
            title=payload.title,
            report_type=payload.report_type,
            report_code=f"RPT-{uuid.uuid4().hex[:10].upper()}",
            description=payload.description,
            from_date=payload.from_date,
            to_date=payload.to_date,
            file_format=payload.file_format,
            status="PENDING",
            progress=0,
        )

        return await self.repository.create(report)

    # Get Report
    async def get_report(
        self,
        report_id: UUID,
    ):

        report = await self.repository.get_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        return report

    # List Reports
    async def get_reports(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        return await self.repository.get_all(
            corporate_account_id,
            skip,
            limit,
        )

    # Update Report
    async def update_report(
        self,
        report_id: UUID,
        payload: ReportUpdate,
    ):

        report = await self.repository.get_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        data = payload.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(report, key, value)

        return await self.repository.update(report)

    # Delete Report
    async def delete_report(
        self,
        report_id: UUID,
    ):

        report = await self.repository.get_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        await self.repository.delete(report)

        return {
            "message": "Report deleted successfully."
        }

    # Download Report
    async def download_report(
        self,
        report_id: UUID,
    ):

        report = await self.repository.get_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found.",
            )

        if not report.can_download:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report is not ready for download.",
            )

        report.last_downloaded_at = datetime.utcnow()

        await self.repository.mark_downloaded(report)

        return {
            "file_name": report.file_name,
            "file_path": report.file_path,
            "download_count": report.download_count,
        }

    # Report Statistics
    async def statistics(
        self,
        corporate_account_id: UUID,
    ):

        return await self.repository.get_statistics(
            corporate_account_id
        )

    # Recent Reports
    async def recent_reports(
        self,
        corporate_account_id: UUID,
        limit: int = 10,
    ):

        return await self.repository.get_recent_reports(
            corporate_account_id,
            limit,
        )

    # Reports By Status
    async def reports_by_status(
        self,
        corporate_account_id: UUID,
        status: str,
    ):

        return await self.repository.get_by_status(
            corporate_account_id,
            status,
        )