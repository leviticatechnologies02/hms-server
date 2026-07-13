from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.schemas.user import PlatformUserCreate, UserCreate
from app.services.user import UserService
from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....core.security import get_password_hash, validate_password_strength
from ....models.user import User
from ....models.role import Role
from ....schemas.common import ResponseModel
from ....core.exceptions import NotFoundException, DuplicateResourceException, BusinessRuleException
from ....core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Super Admin - Platform Users"])


@router.get("/", response_model=ResponseModel)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """List all platform users."""
    query = db.query(User).filter(
        User.user_type == "platform_user",
        User.is_deleted == False
    )
    
    if search:
        query = query.filter(
            User.full_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%")
        )
    
    if role:
        query = query.filter(User.role_name == role)
    
    total = query.count()
    skip = (page - 1) * limit
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return ResponseModel(
        success=True,
        message="Users retrieved successfully",
        data={
            "items": [
                {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role_name,
                    "is_active": user.is_active,
                    "last_login": user.last_login,
                    "created_at": user.created_at
                }
                for user in users
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
    )


@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_platform_user(
    data: PlatformUserCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new platform user (Super Admin only)."""

    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise DuplicateResourceException("User", "email", data.email)

    # Check if username already exists
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise DuplicateResourceException("User", "username", data.username)

    # Validate password
    is_valid, message = validate_password_strength(data.password)
    if not is_valid:
        raise BusinessRuleException(message)

    # Create user
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        user_type="platform_user",
        #hospital_id=data.hospital_id,
        role_name=data.role_name,
        language=data.language,
        timezone=data.timezone,
        preferences=data.preferences,
        is_verified=True,
        created_by=current_user.id
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign Role
    if data.role_id:
        role = db.query(Role).filter(Role.id == data.role_id).first()

        if not role:
            raise NotFoundException("Role", str(data.role_id))

        user.roles.append(role)
        db.commit()
        db.refresh(user)

    # Audit Log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_platform_user",
        resource_type="user",
        resource_id=user.id,
        resource_data={
            "email": user.email,
            "username": user.username,
            "role": user.role_name
        }
    )

    return ResponseModel(
        success=True,
        message="Platform user created successfully",
        data={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role_name,
            "is_verified": user.is_verified,
            "created_at": user.created_at
        }
    )

@router.get("/{user_id}", response_model=ResponseModel)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get user details."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise NotFoundException("User", str(user_id))
    
    return ResponseModel(
        success=True,
        message="User retrieved successfully",
        data={
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "username": user.username,
            "phone": user.phone,
            "role": user.role_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
    )


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: UUID,
    data: dict,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Update user details."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise NotFoundException("User", str(user_id))
    
    # Update fields
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "role_name" in data:
        user.role_name = data["role_name"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    
    user.updated_by = current_user.id
    db.commit()
    db.refresh(user)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update_user",
        resource_type="user",
        resource_id=user_id,
        changes=data,
        resource_data={"email": user.email}
    )
    
    return ResponseModel(
        success=True,
        message="User updated successfully",
        data={
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role_name,
            "is_active": user.is_active
        }
    )


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Soft delete a user."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise NotFoundException("User", str(user_id))
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise BusinessRuleException("Cannot delete your own account")
    
    # Soft delete
    user.is_deleted = True
    user.is_active = False
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete_user",
        resource_type="user",
        resource_id=user_id,
        resource_data={"email": user.email}
    )
    
    return ResponseModel(
        success=True,
        message="User deleted successfully"
    )


@router.post("/{user_id}/activate", response_model=ResponseModel)
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Activate a user."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise NotFoundException("User", str(user_id))
    
    user.is_active = True
    user.updated_by = current_user.id
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="activate_user",
        resource_type="user",
        resource_id=user_id,
        resource_data={"email": user.email}
    )
    
    return ResponseModel(
        success=True,
        message="User activated successfully",
        data={"email": user.email}
    )


@router.post("/{user_id}/deactivate", response_model=ResponseModel)
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Deactivate a user."""
    user = db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()
    
    if not user:
        raise NotFoundException("User", str(user_id))
    
    # Prevent deactivating self
    if user.id == current_user.id:
        raise BusinessRuleException("Cannot deactivate your own account")
    
    user.is_active = False
    user.updated_by = current_user.id
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="deactivate_user",
        resource_type="user",
        resource_id=user_id,
        resource_data={"email": user.email}
    )
    
    return ResponseModel(
        success=True,
        message="User deactivated successfully"
    )


@router.post("/{user_id}/assign-role", response_model=ResponseModel)
async def assign_role(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Assign a role to a user."""
    service = UserService(db)
    service.assign_role_to_user(user_id, role_id, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Role assigned successfully"
    )


@router.post("/{user_id}/remove-role", response_model=ResponseModel)
async def remove_role(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Remove a role from a user."""
    service = UserService(db)
    service.remove_role_from_user(user_id, role_id, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Role removed successfully"
    )


@router.get("/{user_id}/login-history", response_model=ResponseModel)
async def get_user_login_history(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get user login history."""
    service = UserService(db)
    history = service.get_user_login_history(user_id, limit)
    
    return ResponseModel(
        success=True,
        message="Login history retrieved successfully",
        data=history
    )


@router.get("/statistics", response_model=ResponseModel)
async def get_user_statistics(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    service = UserService(db)
    stats = service.get_user_statistics()
    
    return ResponseModel(
        success=True,
        message="User statistics retrieved successfully",
        data=stats
    )
