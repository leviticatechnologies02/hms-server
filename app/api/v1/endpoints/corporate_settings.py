from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.corporate_setting import (
    CorporateSettingCreate,
    CorporateSettingUpdate,
    CorporateSettingResponse,
)

from app.services.corporate_setting_service import (
    CorporateSettingService,
)

router = APIRouter(
    prefix="/corporate/settings",
    tags=["Corporate Settings"],
)

# Create Settings
@router.post(
    "",
    response_model=CorporateSettingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_settings(
    payload: CorporateSettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.create(payload)

# Get Settings
@router.get(
    "/{corporate_account_id}",
    response_model=CorporateSettingResponse,
)
async def get_settings(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.get(
        corporate_account_id
    )

# Update Settings
@router.put(
    "/{corporate_account_id}",
    response_model=CorporateSettingResponse,
)
async def update_settings(
    corporate_account_id: UUID,
    payload: CorporateSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.update(
        corporate_account_id,
        payload,
    )

# Delete Settings
@router.delete(
    "/{corporate_account_id}",
)
async def delete_settings(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.delete(
        corporate_account_id
    )

# Enable Email Notifications
@router.patch(
    "/{corporate_account_id}/email/enable",
)
async def enable_email_notifications(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.enable_email_notifications(
        corporate_account_id
    )

# Disable Email Notifications
@router.patch(
    "/{corporate_account_id}/email/disable",
)
async def disable_email_notifications(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.disable_email_notifications(
        corporate_account_id
    )

# Enable Push Notifications
@router.patch(
    "/{corporate_account_id}/push/enable",
)
async def enable_push_notifications(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.enable_push_notifications(
        corporate_account_id
    )

# Disable Push Notifications
@router.patch(
    "/{corporate_account_id}/push/disable",
)
async def disable_push_notifications(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.disable_push_notifications(
        corporate_account_id
    )

# Enable MFA
@router.patch(
    "/{corporate_account_id}/mfa/enable",
)
async def enable_mfa(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.enable_mfa(
        corporate_account_id
    )

# Disable MFA
@router.patch(
    "/{corporate_account_id}/mfa/disable",
)
async def disable_mfa(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.disable_mfa(
        corporate_account_id
    )

# Enable Audit Logs
@router.patch(
    "/{corporate_account_id}/audit/enable",
)
async def enable_audit_logs(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.enable_audit_logs(
        corporate_account_id
    )

# Disable Audit Logs
@router.patch(
    "/{corporate_account_id}/audit/disable",
)
async def disable_audit_logs(
    corporate_account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):

    service = CorporateSettingService(db)

    return await service.disable_audit_logs(
        corporate_account_id
    )