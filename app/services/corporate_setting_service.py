# app/services/corporate_setting_service.py

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corporate_setting import CorporateSetting
from app.repositories.corporate_setting_repository import (
    CorporateSettingRepository,
)
from app.schemas.corporate_setting import (
    CorporateSettingCreate,
    CorporateSettingUpdate,
)


class CorporateSettingService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CorporateSettingRepository(db)

    # ==========================================================
    # Create Settings
    # ==========================================================

    async def create(
        self,
        payload: CorporateSettingCreate,
    ):

        existing = await self.repository.get_by_corporate(
            payload.corporate_account_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Corporate settings already exist.",
            )

        setting = CorporateSetting(
            **payload.model_dump()
        )

        return await self.repository.create(
            setting
        )

    # ==========================================================
    # Get Settings
    # ==========================================================

    async def get(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.repository.get_by_corporate(
            corporate_account_id
        )

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate settings not found.",
            )

        return setting

    # Update Settings
    async def update(
        self,
        corporate_account_id: UUID,
        payload: CorporateSettingUpdate,
    ):

        setting = await self.repository.get_by_corporate(
            corporate_account_id
        )

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate settings not found.",
            )

        values = payload.model_dump(
            exclude_unset=True
        )

        for key, value in values.items():
            setattr(
                setting,
                key,
                value,
            )

        return await self.repository.update(
            setting
        )

    # Delete Settings
    async def delete(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.repository.get_by_corporate(
            corporate_account_id
        )

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate settings not found.",
            )

        await self.repository.delete(
            setting
        )

        return {
            "message": "Corporate settings deleted successfully."
        }

    # Enable Email Notifications
    async def enable_email_notifications(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.enable_email_notifications(
            setting
        )

    # Disable Email Notifications
    async def disable_email_notifications(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.disable_email_notifications(
            setting
        )

    # Enable Push Notifications
    async def enable_push_notifications(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.enable_push_notifications(
            setting
        )

    # Disable Push Notifications
    async def disable_push_notifications(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.disable_push_notifications(
            setting
        )

    # Enable MFA
    async def enable_mfa(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.enable_mfa(
            setting
        )

    # Disable MFA
    async def disable_mfa(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.disable_mfa(
            setting
        )

    # Enable Audit Logs
    async def enable_audit_logs(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.enable_audit_logs(
            setting
        )

    # Disable Audit Logs
    async def disable_audit_logs(
        self,
        corporate_account_id: UUID,
    ):

        setting = await self.get(
            corporate_account_id
        )

        return await self.repository.disable_audit_logs(
            setting
        )