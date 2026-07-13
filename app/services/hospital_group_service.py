from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hospital_group import HospitalGroup
from app.repositories.hospital_group_repository import HospitalGroupRepository
from app.repositories.hospital import HospitalRepository

from app.schemas.hospital_group import (
    HospitalGroupCreate,
    HospitalGroupUpdate,
)


class HospitalGroupService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = HospitalGroupRepository(db)
        self.hospital_repository = HospitalRepository(db)

    # Create Group
    async def create(
        self,
        payload: HospitalGroupCreate,
    ):

        existing = await self.repository.get_by_code(
            payload.code
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital group code already exists.",
            )

        group = HospitalGroup(
            **payload.model_dump()
        )

        return await self.repository.create(group)

    # Get Group
    async def get(
        self,
        group_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        return group

    # List Groups
    async def list(
        self,
        corporate_account_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        return await self.repository.get_by_corporate(
            corporate_account_id,
            skip,
            limit,
        )

    # Update Group
    async def update(
        self,
        group_id: UUID,
        payload: HospitalGroupUpdate,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        values = payload.model_dump(
            exclude_unset=True
        )

        for key, value in values.items():
            setattr(group, key, value)

        return await self.repository.update(group)

    # Delete Group
    async def delete(
        self,
        group_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        await self.repository.delete(group)

        return {
            "message": "Hospital group deleted successfully."
        }

    # Assign Hospital
    async def assign_hospital(
        self,
        group_id: UUID,
        hospital_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        hospital = await self.hospital_repository.get_by_id(
            hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

        if hospital.hospital_group_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hospital already assigned to another group.",
            )

        return await self.repository.assign_hospital(
            group,
            hospital,
        )

    # Remove Hospital
    async def remove_hospital(
        self,
        group_id: UUID,
        hospital_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        hospital = await self.hospital_repository.get_by_id(
            hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found.",
            )

        return await self.repository.remove_hospital(
            group,
            hospital,
        )

    # Hospitals
    async def hospitals(
        self,
        group_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        return await self.repository.get_hospitals(
            group_id
        )

    # Search
    async def search(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        return await self.repository.search(
            corporate_account_id,
            keyword,
        )

    # Activate
    async def activate(
        self,
        group_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        return await self.repository.activate(
            group
        )

    # Deactivate
    async def deactivate(
        self,
        group_id: UUID,
    ):

        group = await self.repository.get_by_id(
            group_id
        )

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital group not found.",
            )

        return await self.repository.deactivate(
            group
        )

    # Count
    async def count(
        self,
        corporate_account_id: UUID,
    ):

        return await self.repository.count(
            corporate_account_id
        )