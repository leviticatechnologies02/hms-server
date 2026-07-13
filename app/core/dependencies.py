from fastapi import Depends, Request, status
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError
from .database import get_db
from .security import decode_token
from .exceptions import UnauthorizedException, ForbiddenException
from ..models.user import User
from ..models.role import Permission, Role
from ..repositories.user import UserRepository
import logging
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials

    payload = decode_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User inactive")

    return user

async def get_current_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current authenticated super admin."""
    if current_user.role_name != "super_admin":
        raise ForbiddenException("Super admin access required")
    return current_user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise UnauthorizedException("User account is disabled")
    return current_user


def require_permission(permission_name: str):
    """Dependency factory for permission checking."""
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> bool:
        # Super admin has all permissions
        if current_user.role_name == "super_admin":
            return True
        
        # Check user's permissions
        user_repo = UserRepository(db)
        user = user_repo.get_user_with_permissions(current_user.id)
        
        if not user:
            raise ForbiddenException("User not found")
        
        # Check if user has the required permission
        has_permission = False
        for role in user.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    has_permission = True
                    break
            if has_permission:
                break
        
        if not has_permission:
            raise ForbiddenException(f"Permission '{permission_name}' required")
        
        return True
    
    return check_permission


async def get_current_hospital(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[str]:
    """Get current hospital ID from header."""
    hospital_id = request.headers.get("Hospital-ID")
    if hospital_id:
        # Validate hospital exists and is active
        from ..repositories.hospital import HospitalRepository
        hospital_repo = HospitalRepository(db)
        hospital = hospital_repo.get_by_id(hospital_id)
        if not hospital or not hospital.is_active:
            raise ForbiddenException("Invalid or inactive hospital")
        return hospital_id
    return None