from typing import Optional
from uuid import UUID
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.exceptions import DuplicateResourceException
from ..models.hospital import Hospital
from .base import BaseRepository
from sqlalchemy.orm import selectinload
from ..models.subscription import Subscription

class HospitalRepository(BaseRepository):
    """Hospital Repository"""
    def __init__(self, db: AsyncSession):
        super().__init__(db, Hospital)

    # Get By Code
    async def get_by_code(
        self,
        code: str,
    ) -> Optional[Hospital]:

        result = await self.db.execute(
            select(Hospital).where(
                Hospital.code == code
            )
        )

        return result.scalar_one_or_none()

    # Get By Email
    async def get_by_email(
        self,
        email: str,
    ) -> Optional[Hospital]:

        result = await self.db.execute(
            select(Hospital).where(
                Hospital.email == email
            )
        )

        return result.scalar_one_or_none()

    # Get Hospital With Subscription
    async def get_with_subscription(
        self,
        hospital_id: UUID,
    ) -> Optional[Hospital]:

        result = await self.db.execute(
            select(Hospital)
            .options(
                selectinload(Hospital.subscription)
                .selectinload(Subscription.plan)
            )
            .where(
                Hospital.id == hospital_id,
                Hospital.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()
    

    # Create Hospital
    async def create_hospital(
        self,
        data: dict,
    ) -> Hospital:

        existing = await self.get_by_code(
            data["code"]
        )

        if existing:
            raise DuplicateResourceException(
                "Hospital",
                "code",
                data["code"],
            )
        existing = await self.get_by_email(
            data["email"]
        )
        if existing:
            raise DuplicateResourceException(
                "Hospital",
                "email",
                data["email"],
            )
        return await self.create(**data)

    # Search Hospitals
    async def search_hospitals(
        self,
        query: str,
    ):

        result = await self.db.execute(
            select(Hospital).where(
                Hospital.is_deleted == False,
                or_(
                    Hospital.name.ilike(f"%{query}%"),
                    Hospital.code.ilike(f"%{query}%"),
                    Hospital.email.ilike(f"%{query}%"),
                ),
            )
        )

        return result.scalars().all()

    # Active Hospitals
    async def get_active_hospitals(
        self,
    ):
        result = await self.db.execute(
            select(Hospital).where(
                Hospital.is_active == True,
                Hospital.is_deleted == False,
            )
        )
        return result.scalars().all()