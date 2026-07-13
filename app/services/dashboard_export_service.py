import csv
import io
from datetime import datetime

from fastapi import HTTPException
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
)

from app.repositories.analytics_repository import AnalyticsRepository


class DashboardExportService:

    def __init__(self, db):
        self.analytics_repository = AnalyticsRepository(db)

    # Export PDF
    async def export_pdf(
        self,
        corporate_account_id,
    ):

        summary = await self.analytics_repository.get_dashboard_summary(
            corporate_account_id
        )

        buffer = io.BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
        )

        table_data = [
            ["Metric", "Value"],
            ["Hospital Groups", summary.groups],
            ["Hospitals", summary.hospitals],
            ["Doctors", summary[2]],
            ["Staff", summary[3]],
            ["Patients", summary[4]],
            ["Revenue", summary[5]],
            ["Expenses", summary[6]],
            ["Profit", summary[7]],
        ]

        table = Table(table_data)

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )

        document.build([table])

        buffer.seek(0)

        return {
            "filename": f"dashboard_{datetime.utcnow().date()}.pdf",
            "content": buffer.getvalue(),
            "content_type": "application/pdf",
        }

    # Export Excel
    async def export_excel(
        self,
        corporate_account_id,
    ):

        summary = await self.analytics_repository.get_dashboard_summary(
            corporate_account_id
        )

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Corporate Dashboard"

        sheet.append(["Metric", "Value"])
        sheet.append(["Hospital Groups", summary.groups])
        sheet.append(["Hospitals", summary.hospitals])
        sheet.append(["Doctors", summary[2]])
        sheet.append(["Staff", summary[3]])
        sheet.append(["Patients", summary[4]])
        sheet.append(["Revenue", summary[5]])
        sheet.append(["Expenses", summary[6]])
        sheet.append(["Profit", summary[7]])

        buffer = io.BytesIO()

        workbook.save(buffer)

        buffer.seek(0)

        return {
            "filename": f"dashboard_{datetime.utcnow().date()}.xlsx",
            "content": buffer.getvalue(),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    # Export CSV
    async def export_csv(
        self,
        corporate_account_id,
    ):

        summary = await self.analytics_repository.get_dashboard_summary(
            corporate_account_id
        )

        buffer = io.StringIO()

        writer = csv.writer(buffer)

        writer.writerow(["Metric", "Value"])

        writer.writerow(["Hospital Groups", summary.groups])
        writer.writerow(["Hospitals", summary.hospitals])
        writer.writerow(["Doctors", summary[2]])
        writer.writerow(["Staff", summary[3]])
        writer.writerow(["Patients", summary[4]])
        writer.writerow(["Revenue", summary[5]])
        writer.writerow(["Expenses", summary[6]])
        writer.writerow(["Profit", summary[7]])

        return {
            "filename": f"dashboard_{datetime.utcnow().date()}.csv",
            "content": buffer.getvalue(),
            "content_type": "text/csv",
        }

    # Export Dispatcher
    async def export(
        self,
        corporate_account_id,
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

        raise HTTPException(
            status_code=400,
            detail="Invalid export type.",
        )