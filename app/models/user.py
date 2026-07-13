from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel, SoftDeleteMixin, AuditMixin
import uuid


class User(BaseModel, SoftDeleteMixin, AuditMixin):
    """User model."""
    
    __tablename__ = "users"
    
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # User type
    user_type = Column(String(50), nullable=False)  # platform_user, hospital_user, patient
    
    # Hospital association
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=True)
    
    # Role
    role_name = Column(String(50), nullable=False)  # super_admin, hospital_admin, etc.
    
    # Settings
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSON, default={})
    is_verified = Column(Boolean, default=False)
    
    # Security
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    password_history = Column(JSON, default=[])
    
    # Relations
    hospital = relationship("Hospital", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    permissions = relationship("Permission", secondary="user_permissions", back_populates="users")
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserSession(BaseModel):
    """User session model."""
    
    __tablename__ = "user_sessions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(500), nullable=False)
    access_token = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
    
    # Relations
    user = relationship("User", back_populates="sessions")