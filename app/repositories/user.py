from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.user import User
from ..models.role import Role
from ..core.exceptions import DuplicateResourceException
from .base import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:

        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:

        result = await self.db.execute(
            select(User).where(User.username == username)
        )

        return result.scalar_one_or_none()

    async def get_by_hospital(self, hospital_id: UUID):

        result = await self.db.execute(
            select(User).where(
                User.hospital_id == hospital_id,
                User.is_deleted == False,
            )
        )

        return result.scalars().all()

    async def get_user_with_permissions(
        self,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(User)
            .options(
                joinedload(User.roles).joinedload(Role.permissions)
            )
            .where(User.id == user_id)
        )

        return result.unique().scalar_one_or_none()

    async def create_user(self, data: dict):

        existing = await self.get_by_email(data["email"])

        if existing:
            raise DuplicateResourceException(
                "User",
                "email",
                data["email"],
            )

        existing = await self.get_by_username(
            data["username"]
        )

        if existing:
            raise DuplicateResourceException(
                "User",
                "username",
                data["username"],
            )

        return await self.create(**data)

    async def get_platform_users(self):

        result = await self.db.execute(
            select(User).where(
                User.user_type == "platform_user",
                User.is_deleted == False,
            )
        )

        return result.scalars().all()

    async def get_hospital_users(
        self,
        hospital_id: UUID,
    ):

        result = await self.db.execute(
            select(User).where(
                User.hospital_id == hospital_id,
                User.user_type == "hospital_user",
                User.is_deleted == False,
            )
        )

        return result.scalars().all()