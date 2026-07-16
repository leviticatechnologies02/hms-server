import csv
import io
from datetime import datetime
from typing import Optional
from uuid import UUID
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog

class AuditExportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Get Audit Logs
    async def get_logs(
        self,
        corporate_account_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        query = select(AuditLog).where(
            AuditLog.corporate_account_id
            == corporate_account_id
        )

        if from_date:
            query = query.where(
                AuditLog.created_at >= from_date
            )

        if to_date:
            query = query.where(
                AuditLog.created_at <= to_date
            )

        query = query.order_by(
            AuditLog.created_at.desc()
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    # Export PDF
    async def export_pdf(
        self,
        corporate_account_id: UUID,
    ):
        logs = await self.get_logs(
            corporate_account_id
        )
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
        )

        rows = [
            [
                "User",
                "Action",
                "Module",
                "IP",
                "Created At",
            ]
        ]
        for log in logs:
            rows.append(
                [
                    str(log.user_id),
                    log.action,
                    log.module,
                    log.ip_address,
                    str(log.created_at),
                ]
            )
        table = Table(rows)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ]
            )
        )

        pdf.build([table])

        buffer.seek(0)

        return {
            "filename": "audit_logs.pdf",
            "content": buffer.getvalue(),
            "content_type": "application/pdf",
        }

    # Export Excel
    async def export_excel(
        self,
        corporate_account_id: UUID,
    ):

        logs = await self.get_logs(
            corporate_account_id
        )
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Audit Logs"
        sheet.append(
            [
                "User",
                "Action",
                "Module",
                "IP Address",
                "Created At",
            ]
        )

        for log in logs:

            sheet.append(
                [
                    str(log.user_id),
                    log.action,
                    log.module,
                    log.ip_address,
                    str(log.created_at),
                ]
            )

        buffer = io.BytesIO()

        workbook.save(buffer)

        buffer.seek(0)

        return {
            "filename": "audit_logs.xlsx",
            "content": buffer.getvalue(),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    # Export CSV
    async def export_csv(
        self,
        corporate_account_id: UUID,
    ):

        logs = await self.get_logs(
            corporate_account_id
        )

        buffer = io.StringIO()

        writer = csv.writer(buffer)

        writer.writerow(
            [
                "User",
                "Action",
                "Module",
                "IP Address",
                "Created At",
            ]
        )

        for log in logs:

            writer.writerow(
                [
                    str(log.user_id),
                    log.action,
                    log.module,
                    log.ip_address,
                    log.created_at,
                ]
            )

        return {
            "filename": "audit_logs.csv",
            "content": buffer.getvalue(),
            "content_type": "text/csv",
        }

    # Export
    async def export(
        self,
        corporate_account_id: UUID,
        export_type: str,
    ):

        export_type = export_type.lower()

        if export_type == "pdf":
            return await self.export_pdf(
                corporate_account_id
            )

        if export_type == "excel":
            return await self.export_excel(
                corporate_account_id
            )

        if export_type == "csv":
            return await self.export_csv(
                corporate_account_id
            )

        raise ValueError(
            "Invalid export type."
        )