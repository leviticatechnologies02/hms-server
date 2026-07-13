from datetime import datetime, date
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# Generate Report
class ReportGenerateRequest(BaseModel):
    corporate_account_id: UUID

    report_type: str = Field(
        ...,
        description="revenue | patient | finance | appointments | doctors | custom"
    )

    title: str

    from_date: date
    to_date: date

    hospital_group_id: Optional[UUID] = None
    hospital_id: Optional[UUID] = None

    file_format: str = Field(default="pdf")

    description: Optional[str] = None

# Update Report
class ReportUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None

    file_name: Optional[str] = None
    file_path: Optional[str] = None

    error_message: Optional[str] = None

    expires_at: Optional[datetime] = None

# Report Response
class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    corporate_account_id: UUID
    generated_by: UUID

    title: str
    report_type: str
    report_code: str

    description: Optional[str]

    from_date: Optional[datetime]
    to_date: Optional[datetime]

    file_name: Optional[str]
    file_path: Optional[str]
    file_size: int
    file_format: str

    status: str
    progress: int

    is_downloaded: bool
    download_count: int

    last_downloaded_at: Optional[datetime]
    expires_at: Optional[datetime]

    error_message: Optional[str]

    is_completed: bool
    is_failed: bool
    is_pending: bool
    can_download: bool

    created_at: datetime
    updated_at: datetime

# Report List
class ReportListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    title: str
    report_type: str
    report_code: str

    status: str

    file_format: str
    file_size: int

    progress: int

    is_downloaded: bool
    download_count: int

    created_at: datetime

# Download Report
class DownloadReportResponse(BaseModel):
    file_name: str
    file_path: str
    download_url: str

# Report Statistics
class ReportStatistics(BaseModel):
    total_reports: int

    completed_reports: int
    pending_reports: int
    failed_reports: int

    downloaded_reports: int

    total_downloads: int

# Report Filters
class ReportFilter(BaseModel):
    report_type: Optional[str] = None

    status: Optional[str] = None

    from_date: Optional[date] = None
    to_date: Optional[date] = None

    generated_by: Optional[UUID] = None