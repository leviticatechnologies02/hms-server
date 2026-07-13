from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corporate_setting import CorporateSetting


class CorporateSettingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        setting: CorporateSetting,
    ) -> CorporateSetting:

        self.db.add(setting)

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Get By Corporate
    async def get_by_corporate(
        self,
        corporate_account_id: UUID,
    ) -> Optional[CorporateSetting]:

        result = await self.db.execute(
            select(CorporateSetting).where(
                CorporateSetting.corporate_account_id
                == corporate_account_id,
                CorporateSetting.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # Get By ID
    async def get_by_id(
        self,
        setting_id: UUID,
    ) -> Optional[CorporateSetting]:

        result = await self.db.execute(
            select(CorporateSetting).where(
                CorporateSetting.id == setting_id,
                CorporateSetting.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # Update
    async def update(
        self,
        setting: CorporateSetting,
    ) -> CorporateSetting:

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Delete
    async def delete(
        self,
        setting: CorporateSetting,
    ):

        setting.is_active = False

        await self.db.commit()

    # Enable Email Notifications
    async def enable_email_notifications(
        self,
        setting: CorporateSetting,
    ):

        setting.email_notifications = True

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Disable Email Notifications
    async def disable_email_notifications(
        self,
        setting: CorporateSetting,
    ):

        setting.email_notifications = False

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Enable Push Notifications
    async def enable_push_notifications(
        self,
        setting: CorporateSetting,
    ):

        setting.push_notifications = True

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Disable Push Notifications
    async def disable_push_notifications(
        self,
        setting: CorporateSetting,
    ):

        setting.push_notifications = False

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Enable MFA
    async def enable_mfa(
        self,
        setting: CorporateSetting,
    ):

        setting.mfa_enabled = True

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Disable MFA
    async def disable_mfa(
        self,
        setting: CorporateSetting,
    ):

        setting.mfa_enabled = False

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Enable Audit Logs
    async def enable_audit_logs(
        self,
        setting: CorporateSetting,
    ):

        setting.enable_audit_logs = True

        await self.db.commit()
        await self.db.refresh(setting)

        return setting

    # Disable Audit Logs
    async def disable_audit_logs(
        self,
        setting: CorporateSetting,
    ):

        setting.enable_audit_logs = False

        await self.db.commit()
        await self.db.refresh(setting)

        return setting