import logging
from sqlalchemy.orm import selectinload

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import AsyncSessionLocal

from app.models.user import User
from app.models.role import Role, Permission
from app.models.subscription import SubscriptionPlan

logger = logging.getLogger(__name__)


async def seed_database(db: AsyncSession):
    logger.info("Starting database seeding...")

    # ==========================================================
    # Super Admin Role
    # ==========================================================

    # result = await db.execute(
    #     select(Role).where(Role.name == "super_admin")
    # )
    # super_admin_role = result.scalar_one_or_none()
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.name == "super_admin")
    )

    super_admin_role = result.scalar_one_or_none()

    if not super_admin_role:
        super_admin_role = Role(
            name="super_admin",
            description="Super Administrator",
            is_system_role=True,
        )

        db.add(super_admin_role)
        await db.commit()
        await db.refresh(super_admin_role)

        logger.info("Super Admin role created.")

    # ==========================================================
    # Permissions
    # ==========================================================

    permissions = [
        {"name": "hospital.read", "resource": "hospital", "action": "read"},
        {"name": "hospital.create", "resource": "hospital", "action": "create"},
        {"name": "hospital.update", "resource": "hospital", "action": "update"},
        {"name": "hospital.delete", "resource": "hospital", "action": "delete"},

        {"name": "subscription.read", "resource": "subscription", "action": "read"},
        {"name": "subscription.create", "resource": "subscription", "action": "create"},
        {"name": "subscription.update", "resource": "subscription", "action": "update"},
        {"name": "subscription.delete", "resource": "subscription", "action": "delete"},

        {"name": "user.read", "resource": "user", "action": "read"},
        {"name": "user.create", "resource": "user", "action": "create"},
        {"name": "user.update", "resource": "user", "action": "update"},
        {"name": "user.delete", "resource": "user", "action": "delete"},

        {"name": "audit.read", "resource": "audit", "action": "read"},
    ]

    for perm in permissions:

        result = await db.execute(
            select(Permission).where(
                Permission.name == perm["name"]
            )
        )

        permission = result.scalar_one_or_none()

        if not permission:
            db.add(
                Permission(
                    **perm,
                    is_system_permission=True,
                )
            )

    await db.commit()

    logger.info("Permissions seeded.")

    # ==========================================================
    # Assign Permissions
    # ==========================================================

    result = await db.execute(
        select(Permission)
    )

    all_permissions = result.scalars().all()

    super_admin_role.permissions = all_permissions

    await db.commit()
    await db.refresh(super_admin_role)

    logger.info("Permissions assigned.")

    # ==========================================================
    # Super Admin User
    # ==========================================================

    result = await db.execute(
        select(User).where(
            User.email == settings.SUPER_ADMIN_EMAIL
        )
    )

    super_admin = result.scalar_one_or_none()

    if not super_admin:

        super_admin = User(
            email=settings.SUPER_ADMIN_EMAIL,
            username="super_admin",
            hashed_password=get_password_hash(
                settings.SUPER_ADMIN_PASSWORD
            ),
            full_name="Super Administrator",
            user_type="platform_user",
            role_name="super_admin",
            is_verified=True,
            is_active=True,
        )

        # db.add(super_admin)

        # await db.commit()
        # await db.refresh(super_admin)

        # super_admin.roles.append(super_admin_role)

        # await db.commit()
        
        super_admin.roles = [super_admin_role]

        db.add(super_admin)

        await db.commit()
        await db.refresh(super_admin)

        logger.info("Super Admin user created.")

    # ==========================================================
    # Subscription Plans
    # ==========================================================

    plans = [
        {
            "name": "Basic Plan",
            "code": "BASIC",
            "description": "Basic plan",
            "price": 499,
            "currency": "INR",
            "duration_days": "30",
            "max_users": 10,
            "max_storage_gb": 50,
            "features": [
                "Basic EMR",
                "Patient Management",
                "Appointments",
            ],
        },
        {
            "name": "Professional Plan",
            "code": "PROFESSIONAL",
            "description": "Professional plan",
            "price": 999,
            "currency": "INR",
            "duration_days": "30",
            "max_users": 50,
            "max_storage_gb": 200,
            "features": [
                "Advanced EMR",
                "Lab Integration",
                "Pharmacy",
                "Billing",
            ],
        },
        {
            "name": "Enterprise Plan",
            "code": "ENTERPRISE",
            "description": "Enterprise plan",
            "price": 1999,
            "currency": "INR",
            "duration_days": "30",
            "max_users": 200,
            "max_storage_gb": 1000,
            "features": [
                "All Features",
                "AI Integration",
                "Advanced Analytics",
                "Custom Reports",
            ],
        },
    ]

    for plan_data in plans:

        result = await db.execute(
            select(SubscriptionPlan).where(
                SubscriptionPlan.code == plan_data["code"]
            )
        )

        existing = result.scalar_one_or_none()

        if not existing:
            db.add(
                SubscriptionPlan(
                    **plan_data
                )
            )

    await db.commit()

    logger.info("Subscription plans seeded.")

    logger.info("Database seeding completed successfully.")


async def run_seed():

    async with AsyncSessionLocal() as db:
        await seed_database(db)


if __name__ == "__main__":

    import asyncio

    asyncio.run(run_seed())