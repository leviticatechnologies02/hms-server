from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.corporate_account import CorporateAccount
from app.models.hospital_group import HospitalGroup


class CorporateRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        corporate: CorporateAccount,
    ) -> CorporateAccount:
        self.db.add(corporate)
        await self.db.commit()
        await self.db.refresh(corporate)
        return corporate
    # Get By ID
    async def get_by_id(
        self,
        corporate_id: UUID,
    ) -> Optional[CorporateAccount]:

        result = await self.db.execute(
            select(CorporateAccount)
            .options(
                selectinload(CorporateAccount.hospital_groups),
                selectinload(CorporateAccount.reports),
            )
            .where(
                CorporateAccount.id == corporate_id,
                CorporateAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # Get By Code
    async def get_by_code(
        self,
        code: str,
    ) -> Optional[CorporateAccount]:

        result = await self.db.execute(
            select(CorporateAccount).where(
                CorporateAccount.code == code,
                CorporateAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # Get By Name
    async def get_by_name(
        self,
        name: str,
    ) -> Optional[CorporateAccount]:

        result = await self.db.execute(
            select(CorporateAccount).where(
                CorporateAccount.name == name,
                CorporateAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # Get By Email
    async def get_by_email(
        self,
        email: str,
    ) -> Optional[CorporateAccount]:

        result = await self.db.execute(
            select(CorporateAccount).where(
                CorporateAccount.email == email,
                CorporateAccount.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # List
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ):

        result = await self.db.execute(
            select(CorporateAccount)
            .where(CorporateAccount.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(CorporateAccount.created_at.desc())
        )

        return result.scalars().all()

    # Count
    async def count(self) -> int:

        result = await self.db.execute(
            select(func.count(CorporateAccount.id)).where(
                CorporateAccount.is_deleted == False
            )
        )

        return result.scalar()

    # Update
    async def update(
        self,
        corporate: CorporateAccount,
    ) -> CorporateAccount:

        await self.db.commit()
        await self.db.refresh(corporate)
        return corporate

    # Delete
    async def delete(
        self,
        corporate: CorporateAccount,
    ):

        corporate.is_deleted = True
        corporate.is_active = False

        await self.db.commit()

    # Activate
    async def activate(
        self,
        corporate: CorporateAccount,
    ):

        corporate.is_active = True

        await self.db.commit()
        await self.db.refresh(corporate)

        return corporate

    # Deactivate
    async def deactivate(
        self,
        corporate: CorporateAccount,
    ):

        corporate.is_active = False

        await self.db.commit()
        await self.db.refresh(corporate)

        return corporate

    # Hospital Groups
    async def get_hospital_groups(
        self,
        corporate_id: UUID,
    ):

        result = await self.db.execute(
            select(HospitalGroup)
            .where(
                HospitalGroup.corporate_account_id == corporate_id,
                HospitalGroup.is_deleted == False,
            )
            .order_by(HospitalGroup.name)
        )

        return result.scalars().all()
