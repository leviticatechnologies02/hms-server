from sqlalchemy import Column, String, Boolean, Table, ForeignKey, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, AuditMixin
import uuid

# Association tables - defined once here
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

user_permissions = Table(
    'user_permissions',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)


class Permission(BaseModel, AuditMixin):
    """Permission model for RBAC."""
    
    __tablename__ = "permissions"
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    resource = Column(String(100), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(50), nullable=True)
    is_system_permission = Column(Boolean, default=False)
    
    # Relations
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    users = relationship("User", secondary=user_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission {self.name}>"


class Role(BaseModel, AuditMixin):
    """Role model for RBAC."""
    
    __tablename__ = "roles"
    
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    is_system_role = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    
    # Relations
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __repr__(self):
        return f"<Role {self.name}>"