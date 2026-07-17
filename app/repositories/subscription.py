from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from ..models.subscription import Subscription, SubscriptionPlan
from ..core.exceptions import BusinessRuleException
from .base import BaseRepository


class SubscriptionPlanRepository(BaseRepository):
    """Subscription plan repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, SubscriptionPlan)

    async def get_by_code(
        self,
        code: str,
    ) -> Optional[SubscriptionPlan]:

        result = await self.db.execute(
            select(SubscriptionPlan).where(
                SubscriptionPlan.code == code
            )
        )

        return result.scalar_one_or_none()

    async def get_active_plans(
        self,
    ) -> List[SubscriptionPlan]:

        result = await self.db.execute(
            select(SubscriptionPlan).where(
                SubscriptionPlan.is_active == True
            )
        )

        return result.scalars().all()


class SubscriptionRepository(BaseRepository):
    """Subscription repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Subscription)

    async def get_by_hospital(
        self,
        hospital_id: UUID,
    ) -> Optional[Subscription]:

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.hospital_id == hospital_id,
                Subscription.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    async def get_active_subscriptions(
        self,
    ) -> List[Subscription]:

        now = datetime.utcnow()

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.is_active == True,
                Subscription.status == "active",
                Subscription.end_date >= now,
            )
        )

        return result.scalars().all()

    async def get_expiring_subscriptions(
        self,
        days: int = 30,
    ) -> List[Subscription]:

        now = datetime.utcnow()
        expiry_date = now + timedelta(days=days)

        result = await self.db.execute(
            select(Subscription).where(
                Subscription.is_active == True,
                Subscription.status == "active",
                Subscription.end_date.between(
                    now,
                    expiry_date,
                ),
            )
        )

        return result.scalars().all()

    async def create_subscription(
        self,
        data: dict,
    ) -> Subscription:

        existing = await self.get_by_hospital(
            data["hospital_id"]
        )

        if existing:
            raise BusinessRuleException(
                "Hospital already has an active subscription"
            )

        return await self.create(**data)
    