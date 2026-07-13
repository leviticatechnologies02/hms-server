from sqlalchemy.orm import Session
from ..models.user import User
from ..models.role import Role, Permission
from ..models.hospital import Hospital
from ..models.subscription import SubscriptionPlan
from ..core.security import get_password_hash
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


def seed_database(db: Session):
    """Seed database with initial data."""
    logger.info("Seeding database...")
    
    # Create super admin role
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        super_admin_role = Role(
            name="super_admin",
            description="Super Administrator",
            is_system_role=True
        )
        db.add(super_admin_role)
        db.commit()
        db.refresh(super_admin_role)
        logger.info("Created super_admin role")
    
    # Create permissions
    permissions = [
        # Hospital permissions
        {"name": "hospital.read", "resource": "hospital", "action": "read"},
        {"name": "hospital.create", "resource": "hospital", "action": "create"},
        {"name": "hospital.update", "resource": "hospital", "action": "update"},
        {"name": "hospital.delete", "resource": "hospital", "action": "delete"},
        
        # Subscription permissions
        {"name": "subscription.read", "resource": "subscription", "action": "read"},
        {"name": "subscription.create", "resource": "subscription", "action": "create"},
        {"name": "subscription.update", "resource": "subscription", "action": "update"},
        {"name": "subscription.delete", "resource": "subscription", "action": "delete"},
        
        # Audit permissions
        {"name": "audit.read", "resource": "audit", "action": "read"},
        
        # User permissions
        {"name": "user.read", "resource": "user", "action": "read"},
        {"name": "user.create", "resource": "user", "action": "create"},
        {"name": "user.update", "resource": "user", "action": "update"},
        {"name": "user.delete", "resource": "user", "action": "delete"},
    ]
    
    for perm_data in permissions:
        permission = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not permission:
            permission = Permission(
                name=perm_data["name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                is_system_permission=True
            )
            db.add(permission)
    
    db.commit()
    logger.info("Created permissions")
    
    # Assign all permissions to super_admin role
    all_permissions = db.query(Permission).all()
    super_admin_role.permissions = all_permissions
    db.commit()
    logger.info("Assigned permissions to super_admin role")
    
    # Create super admin user
    super_admin = db.query(User).filter(User.email == settings.SUPER_ADMIN_EMAIL).first()
    if not super_admin:
        super_admin = User(
            email=settings.SUPER_ADMIN_EMAIL,
            username="super_admin",
            hashed_password=get_password_hash(settings.SUPER_ADMIN_PASSWORD),
            full_name="Super Administrator",
            user_type="platform_user",
            role_name="super_admin",
            is_verified=True,
            is_active=True
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        logger.info("Created super admin user")
        
        # Assign role
        super_admin.roles.append(super_admin_role)
        db.commit()
        logger.info("Assigned role to super admin")
    
    # Create default subscription plans
    plans = [
        {
            "name": "Basic Plan",
            "code": "BASIC",
            "description": "Basic plan for small hospitals",
            "price": 499.00,
            "currency": "INR",
            "duration_days": "monthly",
            "max_users": 10,
            "max_storage_gb": 50,
            "features": ["Basic EMR", "Patient Management", "Appointments"]
        },
        {
            "name": "Professional Plan",
            "code": "PROFESSIONAL",
            "description": "Professional plan for medium hospitals",
            "price": 999.00,
            "currency": "INR",
            "duration_days": "monthly",
            "max_users": 50,
            "max_storage_gb": 200,
            "features": ["Advanced EMR", "Lab Integration", "Pharmacy", "Billing"]
        },
        {
            "name": "Enterprise Plan",
            "code": "ENTERPRISE",
            "description": "Enterprise plan for large hospitals",
            "price": 1999.00,
            "currency": "INR",
            "duration_days": "monthly",
            "max_users": 200,
            "max_storage_gb": 1000,
            "features": ["All Features", "AI Integration", "Advanced Analytics", "Custom Reports"]
        }
    ]
    
    for plan_data in plans:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == plan_data["code"]).first()
        if not plan:
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
    
    db.commit()
    logger.info("Created subscription plans")
    
    logger.info("Database seeding completed!")


if __name__ == "__main__":
    from ..core.database import SessionLocal
    
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()