from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....models.role import Role, Permission
from ....schemas.common import ResponseModel
from ....core.exceptions import BusinessRuleException, NotFoundException, DuplicateResourceException
from ....core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["Super Admin - Roles & Permissions"])


@router.get("/", response_model=ResponseModel)
async def list_roles(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """List all roles."""
    roles = db.query(Role).filter(Role.is_active == True).all()
    
    return ResponseModel(
        success=True,
        message="Roles retrieved successfully",
        data=[
            {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "permissions": [p.name for p in role.permissions]
            }
            for role in roles
        ]
    )


@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: dict,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new role."""
    # Check if role already exists
    existing = db.query(Role).filter(Role.name == data.get("name")).first()
    if existing:
        raise DuplicateResourceException("Role", "name", data.get("name"))
    
    role = Role(
        name=data.get("name"),
        description=data.get("description"),
        is_system_role=False
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # Assign permissions if provided
    if data.get("permission_ids"):
        permissions = db.query(Permission).filter(
            Permission.id.in_(data["permission_ids"])
        ).all()
        role.permissions = permissions
        db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_role",
        resource_type="role",
        resource_id=role.id,
        resource_data={"name": role.name}
    )
    
    return ResponseModel(
        success=True,
        message="Role created successfully",
        data={
            "id": str(role.id),
            "name": role.name,
            "description": role.description
        }
    )


@router.get("/permissions", response_model=ResponseModel)
async def list_permissions(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """List all permissions."""
    permissions = db.query(Permission).filter(Permission.is_active == True).all()
    
    # Group by resource
    grouped = {}
    for perm in permissions:
        if perm.resource not in grouped:
            grouped[perm.resource] = []
        grouped[perm.resource].append({
            "id": str(perm.id),
            "name": perm.name,
            "action": perm.action,
            "description": perm.description
        })
    
    return ResponseModel(
        success=True,
        message="Permissions retrieved successfully",
        data=grouped
    )


@router.post("/permissions", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: dict,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new permission."""
    # Check if permission already exists
    existing = db.query(Permission).filter(Permission.name == data.get("name")).first()
    if existing:
        raise DuplicateResourceException("Permission", "name", data.get("name"))
    
    permission = Permission(
        name=data.get("name"),
        resource=data.get("resource"),
        action=data.get("action"),
        description=data.get("description"),
        is_system_permission=False
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create_permission",
        resource_type="permission",
        resource_id=permission.id,
        resource_data={"name": permission.name}
    )
    
    return ResponseModel(
        success=True,
        message="Permission created successfully",
        data={
            "id": str(permission.id),
            "name": permission.name,
            "resource": permission.resource,
            "action": permission.action
        }
    )


@router.put("/{role_id}/permissions", response_model=ResponseModel)
async def assign_permissions_to_role(
    role_id: UUID,
    data: dict,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Assign permissions to a role."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise NotFoundException("Role", str(role_id))
    
    # Get permissions
    permission_ids = data.get("permission_ids", [])
    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_ids)
    ).all()
    
    # Update role permissions
    role.permissions = permissions
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="assign_permissions",
        resource_type="role",
        resource_id=role_id,
        resource_data={
            "role": role.name,
            "permissions": [p.name for p in permissions]
        }
    )
    
    return ResponseModel(
        success=True,
        message="Permissions assigned successfully",
        data={
            "role": role.name,
            "permissions": [p.name for p in permissions]
        }
    )


@router.delete("/{role_id}", response_model=ResponseModel)
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Delete a role (soft delete)."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise NotFoundException("Role", str(role_id))
    
    if role.is_system_role:
        raise BusinessRuleException("Cannot delete system roles")
    
    role.is_active = False
    db.commit()
    
    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete_role",
        resource_type="role",
        resource_id=role_id,
        resource_data={"name": role.name}
    )
    
    return ResponseModel(
        success=True,
        message="Role deleted successfully"
    )