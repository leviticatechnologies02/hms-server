from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from uuid import UUID
from ..models.role import Role, Permission
from .base import BaseRepository


class RoleRepository(BaseRepository):
    """Role repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, Role)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).filter(Role.name == name).first()
    
    def get_with_permissions(self, role_id: UUID) -> Optional[Role]:
        """Get role with permissions."""
        return self.db.query(Role).options(
            joinedload(Role.permissions)
        ).filter(Role.id == role_id).first()
    
    def get_active_roles(self) -> List[Role]:
        """Get all active roles."""
        return self.db.query(Role).filter(
            Role.is_active == True
        ).all()
    
    def get_system_roles(self) -> List[Role]:
        """Get all system roles."""
        return self.db.query(Role).filter(
            Role.is_system_role == True
        ).all()
    
    def create_role(self, data: dict) -> Role:
        """Create a role."""
        return self.create(**data)
    
    def update_role(self, role_id: UUID, data: dict) -> Role:
        """Update a role."""
        return self.update(role_id, **data)
    
    def assign_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Assign a permission to a role."""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            return False
        
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
        
        return True
    
    def remove_permission(self, role_id: UUID, permission_id: UUID) -> bool:
        """Remove a permission from a role."""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            return False
        
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
        
        return True