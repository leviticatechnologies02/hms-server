from uuid import UUID
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.corporate_account import CorporateAccount
from app.repositories.corporate_repository import CorporateRepository
from app.schemas.corporate import (
    CorporateCreate,
    CorporateUpdate,
)


class CorporateService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CorporateRepository(db)

    # Create Corporate
    async def create(
        self,
        payload: CorporateCreate,
    ) -> CorporateAccount:

        existing = await self.repository.get_by_code(payload.code)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Corporate code already exists.",
            )

        existing = await self.repository.get_by_email(payload.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Corporate email already exists.",
            )

        corporate = CorporateAccount(**payload.model_dump())

        return await self.repository.create(corporate)

    # Get By ID
    async def get_by_id(
        self,
        corporate_id: UUID,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        return corporate

    # List
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ):

        return await self.repository.get_all(skip, limit)

    # Update
    async def update(
        self,
        corporate_id: UUID,
        payload: CorporateUpdate,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        data = payload.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(corporate, key, value)

        return await self.repository.update(corporate)

    # Delete
    async def delete(
        self,
        corporate_id: UUID,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        await self.repository.delete(corporate)

        return {
            "message": "Corporate account deleted successfully."
        }

    # Activate
    async def activate(
        self,
        corporate_id: UUID,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        return await self.repository.activate(corporate)

    # Deactivate
    async def deactivate(
        self,
        corporate_id: UUID,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        return await self.repository.deactivate(corporate)

    # Hospital Groups
    async def hospital_groups(
        self,
        corporate_id: UUID,
    ):

        corporate = await self.repository.get_by_id(corporate_id)

        if not corporate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Corporate account not found.",
            )

        return await self.repository.get_hospital_groups(corporate_id)

    # Count
    async def count(self):

        return await self.repository.count()