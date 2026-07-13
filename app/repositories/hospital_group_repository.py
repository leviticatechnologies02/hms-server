from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hospital_group import HospitalGroup
from app.models.hospital import Hospital


class HospitalGroupRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        group: HospitalGroup,
    ) -> HospitalGroup:

        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)

        return group

    # Get By ID
    async def get_by_id(
        self,
        group_id: UUID,
    ) -> Optional[HospitalGroup]:

        result = await self.db.execute(
            select(HospitalGroup)
            .options(
                selectinload(HospitalGroup.hospitals),
            )
            .where(
                HospitalGroup.id == group_id,
                HospitalGroup.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # Get By Code
    async def get_by_code(
        self,
        code: str,
    ) -> Optional[HospitalGroup]:

        result = await self.db.execute(
            select(HospitalGroup).where(
                HospitalGroup.code == code,
                HospitalGroup.is_deleted == False,
            )
        )

        return result.scalar_one_or_none()

    # List By Corporate
    async def get_by_corporate(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        result = await self.db.execute(
            select(HospitalGroup)
            .where(
                HospitalGroup.corporate_account_id == corporate_account_id,
                HospitalGroup.is_deleted == False,
            )
            .order_by(HospitalGroup.name)
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    # Count
    async def count(
        self,
        corporate_account_id: UUID,
    ) -> int:

        result = await self.db.execute(
            select(func.count(HospitalGroup.id)).where(
                HospitalGroup.corporate_account_id == corporate_account_id,
                HospitalGroup.is_deleted == False,
            )
        )

        return result.scalar()

    # Update
    async def update(
        self,
        group: HospitalGroup,
    ) -> HospitalGroup:

        await self.db.commit()
        await self.db.refresh(group)

        return group

    # Delete
    async def delete(
        self,
        group: HospitalGroup,
    ):

        group.is_deleted = True
        group.is_active = False

        await self.db.commit()

    # Assign Hospital
    async def assign_hospital(
        self,
        group: HospitalGroup,
        hospital: Hospital,
    ):

        hospital.hospital_group_id = group.id

        group.total_hospitals += 1

        await self.db.commit()

        await self.db.refresh(group)

        return group

    # Remove Hospital
    async def remove_hospital(
        self,
        group: HospitalGroup,
        hospital: Hospital,
    ):

        hospital.hospital_group_id = None

        if group.total_hospitals > 0:
            group.total_hospitals -= 1

        await self.db.commit()

        await self.db.refresh(group)

        return group

    # Hospitals
    async def get_hospitals(
        self,
        group_id: UUID,
    ):

        result = await self.db.execute(
            select(Hospital)
            .where(
                Hospital.hospital_group_id == group_id,
                Hospital.is_deleted == False,
            )
            .order_by(Hospital.name)
        )

        return result.scalars().all()

    # Search
    async def search(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        result = await self.db.execute(
            select(HospitalGroup)
            .where(
                HospitalGroup.corporate_account_id == corporate_account_id,
                HospitalGroup.is_deleted == False,
                HospitalGroup.name.ilike(f"%{keyword}%"),
            )
            .order_by(HospitalGroup.name)
        )

        return result.scalars().all()

    # Activate
    async def activate(
        self,
        group: HospitalGroup,
    ):

        group.is_active = True

        await self.db.commit()
        await self.db.refresh(group)

        return group

    # Deactivate
    async def deactivate(
        self,
        group: HospitalGroup,
    ):

        group.is_active = False

        await self.db.commit()
        await self.db.refresh(group)

        return group