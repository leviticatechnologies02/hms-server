from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.models.user import User
from app.repositories.hospital import HospitalRepository
from app.repositories.user import UserRepository
import logging
logger = logging.getLogger(__name__)
security = HTTPBearer()

# Current User
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedException("Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token")
    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise UnauthorizedException("User is inactive")
    return user

# Current Active User
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise UnauthorizedException("User account is disabled")
    return current_user

# Super Admin
async def get_current_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role_name != "super_admin":
        raise ForbiddenException("Super Admin access required")
    return current_user

# Permission Checker
def require_permission(permission_name: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.role_name == "super_admin":
            return True
        user_repo = UserRepository(db)
        user = await user_repo.get_user_with_permissions(
            current_user.id
        )

        if not user:
            raise ForbiddenException("User not found")
        for role in user.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        raise ForbiddenException(
            f"Permission '{permission_name}' required"
        )
    return permission_checker

# Current Hospital
async def get_current_hospital(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[str]:

    hospital_id = request.headers.get("Hospital-ID")
    if not hospital_id:
        return None
    hospital_repo = HospitalRepository(db)
    hospital = await hospital_repo.get_by_id(hospital_id)
    if not hospital:
        raise ForbiddenException("Hospital not found")
    if not hospital.is_active:
        raise ForbiddenException("Hospital is inactive")
    return hospital_id