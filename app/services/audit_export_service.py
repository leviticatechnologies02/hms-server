import csv
import io
from datetime import datetime
from typing import Optional
from uuid import UUID

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditExportService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_logs(
        self,
        corporate_account_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        query = select(AuditLog).where(
            AuditLog.corporate_account_id == corporate_account_id
        )

        if from_date:
            query = query.where(AuditLog.created_at >= from_date)

        if to_date:
            query = query.where(AuditLog.created_at <= to_date)

        query = query.order_by(AuditLog.created_at.desc())

        result = await self.db.execute(query)

        return result.scalars().all()

    async def export_pdf(
        self,
        corporate_account_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        logs = await self.get_logs(
            corporate_account_id,
            from_date,
            to_date,
        )

        buffer = io.BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
        )

        rows = [[
            "User",
            "Action",
            "Module",
            "IP Address",
            "Created At",
        ]]

        for log in logs:
            rows.append([
                str(log.user_id),
                log.action,
                log.module,
                log.ip_address,
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        table = Table(rows)

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ])
        )

        pdf.build([table])

        buffer.seek(0)

        return {
            "filename": "audit_logs.pdf",
            "content": buffer.getvalue(),
            "content_type": "application/pdf",
        }

    async def export_excel(
        self,
        corporate_account_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        logs = await self.get_logs(
            corporate_account_id,
            from_date,
            to_date,
        )

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Audit Logs"

        sheet.append([
            "User",
            "Action",
            "Module",
            "IP Address",
            "Created At",
        ])

        for log in logs:
            sheet.append([
                str(log.user_id),
                log.action,
                log.module,
                log.ip_address,
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        buffer = io.BytesIO()

        workbook.save(buffer)

        buffer.seek(0)

        return {
            "filename": "audit_logs.xlsx",
            "content": buffer.getvalue(),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    async def export_csv(
        self,
        corporate_account_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        logs = await self.get_logs(
            corporate_account_id,
            from_date,
            to_date,
        )

        buffer = io.StringIO()

        writer = csv.writer(buffer)

        writer.writerow([
            "User",
            "Action",
            "Module",
            "IP Address",
            "Created At",
        ])

        for log in logs:
            writer.writerow([
                str(log.user_id),
                log.action,
                log.module,
                log.ip_address,
                log.created_at.isoformat(),
            ])

        return {
            "filename": "audit_logs.csv",
            "content": buffer.getvalue(),
            "content_type": "text/csv",
        }

    async def export(
        self,
        corporate_account_id: UUID,
        export_type: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ):

        export_type = export_type.lower()

        if export_type == "pdf":
            return await self.export_pdf(
                corporate_account_id,
                from_date,
                to_date,
            )

        elif export_type == "excel":
            return await self.export_excel(
                corporate_account_id,
                from_date,
                to_date,
            )

        elif export_type == "csv":
            return await self.export_csv(
                corporate_account_id,
                from_date,
                to_date,
            )

        raise ValueError(
            "Supported export types are: pdf, excel, csv."
        )