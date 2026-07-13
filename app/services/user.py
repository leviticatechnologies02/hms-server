from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta

from app.models.hospital import Hospital
from app.models.role import Role
from app.models.user import User, UserSession
from ..repositories.user import UserRepository
from ..repositories.role import RoleRepository
from ..repositories.audit import AuditRepository
from ..schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    UserProfile, UserListResponse, UserRoleAssignment
)
from ..core.exceptions import (
    NotFoundException, DuplicateResourceException, 
    BusinessRuleException, ValidationException
)
from ..core.security import get_password_hash, validate_password_strength
from ..core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User service with comprehensive business logic."""
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.audit_repo = AuditRepository(db)
        self.db = db
    
    def create_user(self, data: UserCreate, created_by: UUID) -> UserResponse:
        """
        Create a new user with validation.
        
        Args:
            data: User creation data
            created_by: ID of the user creating this user
            
        Returns:
            UserResponse: Created user data
            
        Raises:
            DuplicateResourceException: If email or username already exists
            ValidationException: If password is weak or data is invalid
            BusinessRuleException: If business rules are violated
        """
        logger.info(f"Creating user: {data.email}")
        
        # Validate email uniqueness
        existing_email = self.user_repo.get_by_email(data.email)
        if existing_email:
            raise DuplicateResourceException("User", "email", data.email)
        
        # Validate username uniqueness
        existing_username = self.user_repo.get_by_username(data.username)
        if existing_username:
            raise DuplicateResourceException("User", "username", data.username)
        
        # Validate password strength
        if data.password:
            is_valid, message = validate_password_strength(data.password)
            if not is_valid:
                raise ValidationException(message)
        
        # Validate role exists if provided
        if data.role_id:
            role = self.role_repo.get_by_id(data.role_id)
            if not role:
                raise NotFoundException("Role", str(data.role_id))
        
        # Create user
        user_data = data.model_dump(exclude={'password', 'role_id'})
        user_data['hashed_password'] = get_password_hash(data.password)
        user_data['created_by'] = created_by
        user_data['password_changed_at'] = datetime.utcnow()
        
        user = self.user_repo.create(**user_data)
        
        # Assign role if provided
        if data.role_id:
            role = self.role_repo.get_by_id(data.role_id)
            if role:
                user.roles.append(role)
                self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=created_by,
            action="create_user",
            resource_type="user",
            resource_id=user.id,
            resource_data={
                "email": user.email,
                "username": user.username,
                "role": user.role_name
            }
        )
        
        return UserResponse.model_validate(user)
    
    def get_user_by_id(self, user_id: UUID, include_relations: bool = False) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            include_relations: Whether to include roles and permissions
            
        Returns:
            Optional[UserResponse]: User data if found
            
        Raises:
            NotFoundException: If user not found
        """
        if include_relations:
            user = self.user_repo.get_user_with_relations(user_id)
        else:
            user = self.user_repo.get_by_id(user_id)
        
        if not user:
            raise NotFoundException("User", str(user_id))
        
        return UserResponse.model_validate(user)
    
    def get_user_with_permissions(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get user with their roles and permissions.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with user, roles, and permissions
        """
        user = self.user_repo.get_user_with_permissions(user_id)
        if not user:
            return None
        
        # Get all permissions from user's roles
        permissions = set()
        for role in user.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        
        # If user has direct permissions (if implemented)
        for permission in user.permissions:
            permissions.add(permission.name)
        
        return {
            "user": UserResponse.model_validate(user),
            "roles": [role.name for role in user.roles],
            "permissions": list(permissions)
        }
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        hospital_id: Optional[UUID] = None,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[UserResponse], int]:
        """
        Get list of users with filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            search: Search term for email, username, or full_name
            role: Filter by role name
            hospital_id: Filter by hospital ID
            user_type: Filter by user type
            is_active: Filter by active status
            
        Returns:
            Tuple of (users list, total count)
        """
        filters = {}
        if user_type:
            filters['user_type'] = user_type
        if is_active is not None:
            filters['is_active'] = is_active
        
        users = self.user_repo.get_all(skip=skip, limit=limit, **filters)
        total = self.user_repo.get_count(**filters)
        
        # Apply additional filters that can't be done at query level
        filtered_users = []
        for user in users:
            match = True
            
            # Search filter
            if search:
                search_lower = search.lower()
                if not (
                    search_lower in user.email.lower() or
                    search_lower in user.username.lower() or
                    search_lower in user.full_name.lower() or
                    (user.phone and search_lower in user.phone)
                ):
                    match = False
            
            # Role filter
            if role and match:
                if user.role_name != role:
                    match = False
            
            # Hospital filter
            if hospital_id and match:
                if user.hospital_id != hospital_id:
                    match = False
            
            if match:
                filtered_users.append(user)
        
        return [UserResponse.model_validate(u) for u in filtered_users], len(filtered_users)
    
    def update_user(self, user_id: UUID, data: UserUpdate, updated_by: UUID) -> UserResponse:
        """
        Update user details.
        
        Args:
            user_id: User ID
            data: User update data
            updated_by: ID of the user updating
            
        Returns:
            UserResponse: Updated user data
            
        Raises:
            NotFoundException: If user not found
            DuplicateResourceException: If email or username already taken
            BusinessRuleException: If business rules are violated
        """
        logger.info(f"Updating user: {user_id}")
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        # Track changes for audit
        changes = {}
        update_data = data.model_dump(exclude_unset=True)
        
        # Validate email uniqueness if changing
        if 'email' in update_data and update_data['email'] != user.email:
            existing = self.user_repo.get_by_email(update_data['email'])
            if existing:
                raise DuplicateResourceException("User", "email", update_data['email'])
            changes['email'] = {'old': user.email, 'new': update_data['email']}
        
        # Validate username uniqueness if changing
        if 'username' in update_data and update_data['username'] != user.username:
            existing = self.user_repo.get_by_username(update_data['username'])
            if existing:
                raise DuplicateResourceException("User", "username", update_data['username'])
            changes['username'] = {'old': user.username, 'new': update_data['username']}
        
        # Validate role if changing
        if 'role_id' in update_data:
            role = self.role_repo.get_by_id(update_data['role_id'])
            if not role:
                raise NotFoundException("Role", str(update_data['role_id']))
            changes['role'] = {'old': user.role_name, 'new': role.name}
        
        # Update user
        update_data['updated_by'] = updated_by
        updated_user = self.user_repo.update(user_id, **update_data)
        
        # Create audit log
        if changes:
            create_audit_log(
                db=self.db,
                user_id=updated_by,
                action="update_user",
                resource_type="user",
                resource_id=user_id,
                changes=changes,
                resource_data={"email": updated_user.email}
            )
        
        return UserResponse.model_validate(updated_user)
    
    def change_user_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str,
        updated_by: UUID
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            updated_by: ID of the user updating
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            NotFoundException: If user not found
            BusinessRuleException: If current password is incorrect or new password is weak
        """
        from ..core.security import verify_password
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise BusinessRuleException("Current password is incorrect")
        
        # Validate new password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationException(message)
        
        # Check password history
        password_history = user.password_history or []
        for old_password_hash in password_history:
            if verify_password(new_password, old_password_hash):
                raise BusinessRuleException("Password already used recently")
        
        # Update password
        new_password_hash = get_password_hash(new_password)
        user.hashed_password = new_password_hash
        user.password_changed_at = datetime.utcnow()
        user.updated_by = updated_by
        
        # Update password history
        if len(password_history) >= 5:
            password_history.pop(0)
        password_history.append(new_password_hash)
        user.password_history = password_history
        
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=updated_by,
            action="change_password",
            resource_type="user",
            resource_id=user_id,
            resource_data={"email": user.email}
        )
        
        return True
    
    def reset_user_password(self, user_id: UUID, new_password: str, updated_by: UUID) -> bool:
        """
        Reset user password (admin action).
        
        Args:
            user_id: User ID
            new_password: New password
            updated_by: ID of the user updating
            
        Returns:
            bool: True if password reset successfully
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        # Validate new password strength
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            raise ValidationException(message)
        
        # Update password
        new_password_hash = get_password_hash(new_password)
        user.hashed_password = new_password_hash
        user.password_changed_at = datetime.utcnow()
        user.updated_by = updated_by
        
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=updated_by,
            action="reset_user_password",
            resource_type="user",
            resource_id=user_id,
            resource_data={"email": user.email}
        )
        
        return True
    
    def assign_role_to_user(self, user_id: UUID, role_id: UUID, assigned_by: UUID) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            assigned_by: ID of the user assigning
            
        Returns:
            bool: True if role assigned successfully
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", str(role_id))
        
        # Check if user already has this role
        if role in user.roles:
            raise BusinessRuleException("User already has this role")
        
        # Assign role
        user.roles.append(role)
        user.role_name = role.name  # Update primary role
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=assigned_by,
            action="assign_role",
            resource_type="user",
            resource_id=user_id,
            resource_data={
                "user": user.email,
                "role": role.name
            }
        )
        
        return True
    
    def remove_role_from_user(self, user_id: UUID, role_id: UUID, removed_by: UUID) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: User ID
            role_id: Role ID
            removed_by: ID of the user removing
            
        Returns:
            bool: True if role removed successfully
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role", str(role_id))
        
        # Check if user has this role
        if role not in user.roles:
            raise BusinessRuleException("User does not have this role")
        
        # Can't remove last role
        if len(user.roles) <= 1:
            raise BusinessRuleException("User must have at least one role")
        
        # Remove role
        user.roles.remove(role)
        
        # Update primary role if needed
        if user.role_name == role.name and user.roles:
            user.role_name = user.roles[0].name
        
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=removed_by,
            action="remove_role",
            resource_type="user",
            resource_id=user_id,
            resource_data={
                "user": user.email,
                "role": role.name
            }
        )
        
        return True
    
    def activate_user(self, user_id: UUID, activated_by: UUID) -> UserResponse:
        """
        Activate a user account.
        
        Args:
            user_id: User ID
            activated_by: ID of the user activating
            
        Returns:
            UserResponse: Updated user data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        if user.is_active:
            raise BusinessRuleException("User is already active")
        
        user.is_active = True
        user.updated_by = activated_by
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=activated_by,
            action="activate_user",
            resource_type="user",
            resource_id=user_id,
            resource_data={"email": user.email}
        )
        
        return UserResponse.model_validate(user)
    
    def deactivate_user(self, user_id: UUID, deactivated_by: UUID) -> UserResponse:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            deactivated_by: ID of the user deactivating
            
        Returns:
            UserResponse: Updated user data
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        if not user.is_active:
            raise BusinessRuleException("User is already inactive")
        
        # Prevent deactivating self
        if user_id == deactivated_by:
            raise BusinessRuleException("Cannot deactivate your own account")
        
        user.is_active = False
        user.updated_by = deactivated_by
        self.db.commit()
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=deactivated_by,
            action="deactivate_user",
            resource_type="user",
            resource_id=user_id,
            resource_data={"email": user.email}
        )
        
        return UserResponse.model_validate(user)
    
    def delete_user(self, user_id: UUID, deleted_by: UUID, hard_delete: bool = False) -> bool:
        """
        Delete a user (soft or hard).
        
        Args:
            user_id: User ID
            deleted_by: ID of the user deleting
            hard_delete: Whether to hard delete
            
        Returns:
            bool: True if deleted successfully
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
        
        # Prevent deleting self
        if user_id == deleted_by:
            raise BusinessRuleException("Cannot delete your own account")
        
        # Check if user has active sessions
        if not hard_delete:
            active_sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_valid == True
            ).count()
            if active_sessions > 0:
                raise BusinessRuleException("Cannot delete user with active sessions. Deactivate first.")
        
        # Delete user
        result = self.user_repo.delete(user_id, hard_delete=hard_delete)
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=deleted_by,
            action="delete_user",
            resource_type="user",
            resource_id=user_id,
            resource_data={"email": user.email}
        )
        
        return result
    
    def get_user_login_history(self, user_id: UUID, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user login history.
        
        Args:
            user_id: User ID
            limit: Maximum records to return
            
        Returns:
            List of login history entries
        """
        logs = self.audit_repo.get_by_user(user_id, limit=limit)
        history = []
        for log in logs:
            if log.action in ['login_success', 'login_failed']:
                history.append({
                    'timestamp': log.created_at,
                    'action': log.action,
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'status': log.status
                })
        return history
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dict with user statistics
        """
        total_users = self.user_repo.get_count()
        active_users = self.user_repo.get_count(is_active=True)
        inactive_users = total_users - active_users
        
        # Get users by role
        role_stats = {}
        roles = self.db.query(Role).all()
        for role in roles:
            count = self.db.query(User).filter(
                User.role_name == role.name,
                User.is_deleted == False
            ).count()
            if count > 0:
                role_stats[role.name] = count
        
        # Get users by hospital (for hospital admin)
        hospital_stats = {}
        hospitals = self.db.query(Hospital).filter(
            Hospital.is_deleted == False
        ).all()
        for hospital in hospitals:
            count = self.db.query(User).filter(
                User.hospital_id == hospital.id,
                User.is_deleted == False
            ).count()
            if count > 0:
                hospital_stats[hospital.name] = count
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'users_by_role': role_stats,
            'users_by_hospital': hospital_stats,
            'created_today': self.user_repo.get_count(created_at=datetime.utcnow().date())
        }