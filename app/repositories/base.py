from uuid import UUID
from typing import Type, TypeVar, Optional, List

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import NotFoundException

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:

    def __init__(
        self,
        db: AsyncSession,
        model: Type[ModelType],
    ):
        self.db = db
        self.model = model

    async def get_by_id(
        self,
        id: UUID,
    ) -> Optional[ModelType]:

        result = await self.db.execute(
            select(self.model).where(
                self.model.id == id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id_or_fail(
        self,
        id: UUID,
    ):

        record = await self.get_by_id(id)

        if not record:
            raise NotFoundException(
                self.model.__name__,
                str(id),
            )

        return record

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters,
    ):

        query = select(self.model)

        for key, value in filters.items():
            if value is not None:
                query = query.where(
                    getattr(self.model, key) == value
                )

        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_count(
        self,
        **filters,
    ):

        query = select(
            func.count()
        ).select_from(self.model)

        for key, value in filters.items():
            if value is not None:
                query = query.where(
                    getattr(self.model, key) == value
                )

        result = await self.db.execute(query)

        return result.scalar()

    async def create(
        self,
        **kwargs,
    ):

        record = self.model(**kwargs)

        self.db.add(record)

        await self.db.commit()
        await self.db.refresh(record)

        return record

    async def update(
        self,
        id: UUID,
        **kwargs,
    ):

        record = await self.get_by_id_or_fail(id)

        for key, value in kwargs.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)

        await self.db.commit()
        await self.db.refresh(record)

        return record

    async def delete(
        self,
        id: UUID,
        hard_delete: bool = False,
    ):

        record = await self.get_by_id_or_fail(id)

        if hard_delete:
            await self.db.delete(record)

        else:
            if hasattr(record, "is_deleted"):
                record.is_deleted = True

        await self.db.commit()

        return True

    async def search(
        self,
        search_field: str,
        search_value: str,
        **filters,
    ):

        query = select(self.model)

        if search_field and search_value:
            query = query.where(
                getattr(self.model, search_field).ilike(
                    f"%{search_value}%"
                )
            )

        for key, value in filters.items():
            if value is not None:
                query = query.where(
                    getattr(self.model, key) == value
                )

        result = await self.db.execute(query)

        return result.scalars().all()