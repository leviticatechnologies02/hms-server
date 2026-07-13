from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..models.role import Permission
from .base import BaseRepository


class PermissionRepository(BaseRepository):
    """Permission repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, Permission)
    
    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.db.query(Permission).filter(Permission.name == name).first()
    
    def get_by_resource(self, resource: str) -> List[Permission]:
        """Get permissions by resource."""
        return self.db.query(Permission).filter(
            Permission.resource == resource
        ).all()
    
    def get_by_category(self, category: str) -> List[Permission]:
        """Get permissions by category."""
        return self.db.query(Permission).filter(
            Permission.category == category
        ).all()
    
    def get_active_permissions(self) -> List[Permission]:
        """Get all active permissions."""
        return self.db.query(Permission).filter(
            Permission.is_active == True
        ).all()
    
    def get_system_permissions(self) -> List[Permission]:
        """Get all system permissions."""
        return self.db.query(Permission).filter(
            Permission.is_system_permission == True
        ).all()
    
    def create_permission(self, data: dict) -> Permission:
        """Create a permission."""
        return self.create(**data)
    
    def batch_create_permissions(self, permissions_data: List[dict]) -> List[Permission]:
        """Create multiple permissions in batch."""
        permissions = []
        for data in permissions_data:
            existing = self.get_by_name(data.get('name'))
            if not existing:
                permission = self.create(**data)
                permissions.append(permission)
        return permissions