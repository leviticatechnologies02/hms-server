from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any, Generic, TypeVar, Type
from pydantic import BaseModel
from uuid import UUID
from ..core.exceptions import NotFoundException

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_id_or_fail(self, id: UUID) -> ModelType:
        """Get record by ID or raise NotFoundException."""
        record = self.get_by_id(id)
        if not record:
            raise NotFoundException(self.model.__name__, str(id))
        return record
    
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        """Get all records with pagination."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()
    
    def get_count(self, **filters) -> int:
        """Get count of records with filters."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        record = self.model(**kwargs)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def update(self, id: UUID, **kwargs) -> ModelType:
        """Update a record."""
        record = self.get_by_id_or_fail(id)
        for key, value in kwargs.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def delete(self, id: UUID, hard_delete: bool = False) -> bool:
        """Delete a record."""
        record = self.get_by_id_or_fail(id)
        if hard_delete:
            self.db.delete(record)
        else:
            # Soft delete
            if hasattr(record, "is_deleted"):
                record.is_deleted = True
                record.deleted_at = func.now()
        self.db.commit()
        return True
    
    def search(self, search_field: str, search_value: str, **filters) -> List[ModelType]:
        """Search records by field."""
        query = self.db.query(self.model)
        if search_field and search_value:
            query = query.filter(getattr(self.model, search_field).ilike(f"%{search_value}%"))
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.all()