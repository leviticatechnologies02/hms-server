from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from uuid import UUID
from ..models.user import User
from ..models.role import Role
from ..core.exceptions import DuplicateResourceException
from .base import BaseRepository


class UserRepository(BaseRepository):
    """User repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_hospital(self, hospital_id: UUID) -> List[User]:
        """Get users by hospital."""
        return self.db.query(User).filter(
            User.hospital_id == hospital_id,
            User.is_deleted == False
        ).all()
    
    def get_user_with_permissions(self, user_id: UUID) -> Optional[User]:
        """Get user with roles and permissions."""
        return self.db.query(User).options(
            joinedload(User.roles).joinedload(Role.permissions)
        ).filter(User.id == user_id).first()
    
    def create_user(self, data: dict) -> User:
        """Create user with validation."""
        # Check for duplicate email
        existing = self.get_by_email(data.get("email"))
        if existing:
            raise DuplicateResourceException("User", "email", data.get("email"))
        
        # Check for duplicate username
        existing = self.get_by_username(data.get("username"))
        if existing:
            raise DuplicateResourceException("User", "username", data.get("username"))
        
        return self.create(**data)
    
    def get_platform_users(self) -> List[User]:
        """Get platform users (super admins)."""
        return self.db.query(User).filter(
            User.user_type == "platform_user",
            User.is_deleted == False
        ).all()
    
    def get_hospital_users(self, hospital_id: UUID) -> List[User]:
        """Get hospital users."""
        return self.db.query(User).filter(
            User.hospital_id == hospital_id,
            User.user_type == "hospital_user",
            User.is_deleted == False
        ).all()