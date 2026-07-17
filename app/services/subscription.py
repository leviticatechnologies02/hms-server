from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from ..repositories.subscription import (
    SubscriptionRepository,
    SubscriptionPlanRepository,
)
from ..repositories.hospital import HospitalRepository
from ..schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanResponse,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
)
from ..core.exceptions import (
    NotFoundException,
    BusinessRuleException,
)

from ..core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_repo = SubscriptionRepository(db)
        self.plan_repo = SubscriptionPlanRepository(db)
        self.hospital_repo = HospitalRepository(db)

    async def create_plan(
        self,
        data: SubscriptionPlanCreate,
        user_id: UUID,
    ) -> SubscriptionPlanResponse:
        logger.info(f"Creating subscription plan: {data.name}")
        existing = await self.plan_repo.get_by_code(data.code)
        if existing:
            raise BusinessRuleException(
                f"Plan with code '{data.code}' already exists"
            )

        plan_data = data.model_dump()
        plan_data["created_by"] = user_id
        plan = await self.plan_repo.create(**plan_data)
        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="create_subscription_plan",
            resource_type="subscription_plan",
            resource_id=plan.id,
            resource_data={
                "name": plan.name,
                "code": plan.code,
            },
        )

        return SubscriptionPlanResponse.model_validate(plan)

    async def get_plans(
        self,
    ) -> List[SubscriptionPlanResponse]:
        plans = await self.plan_repo.get_active_plans()
        return [
            SubscriptionPlanResponse.model_validate(plan)
            for plan in plans
        ]
    
    async def assign_subscription(
        self,
        data: SubscriptionCreate,
        user_id: UUID,
    ) -> SubscriptionResponse:

        logger.info(
            f"Assigning subscription to hospital {data.hospital_id}"
        )
        hospital = await self.hospital_repo.get_by_id(
            data.hospital_id
        )
        if hospital is None:
            raise NotFoundException(
                "Hospital",
                str(data.hospital_id),
            )
        plan = await self.plan_repo.get_by_id(
            data.plan_id
        )
        if plan is None:
            raise NotFoundException(
                "Subscription Plan",
                str(data.plan_id),
            )
        existing = await self.subscription_repo.get_by_hospital(
            data.hospital_id
        )
        if existing:
            raise BusinessRuleException(
                "Hospital already has an active subscription."
            )
        subscription_data = data.model_dump()
        subscription_data["created_by"] = user_id
        subscription = await self.subscription_repo.create_subscription(
            subscription_data
        )
        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="assign_subscription",
            resource_type="subscription",
            resource_id=subscription.id,
            resource_data={
                "hospital_id": str(data.hospital_id),
                "plan_id": str(data.plan_id),
            },
        )
        return SubscriptionResponse.model_validate(
            subscription
        )
    async def get_hospital_subscription(
        self,
        hospital_id: UUID,
    ) -> Optional[SubscriptionResponse]:
        subscription = await self.subscription_repo.get_by_hospital(
            hospital_id
        )
        if subscription is None:
            return None
        return SubscriptionResponse.model_validate(
            subscription
        )

    async def get_expiring_subscriptions(
        self,
        days: int = 30,
    ) -> List[SubscriptionResponse]:
        subscriptions = (
            await self.subscription_repo.get_expiring_subscriptions(
                days
            )
        )
        return [
            SubscriptionResponse.model_validate(sub)
            for sub in subscriptions
        ]
    async def update_subscription(
        self,
        subscription_id: UUID,
        data: SubscriptionUpdate,
        user_id: UUID,
    ) -> SubscriptionResponse:
        subscription = await self.subscription_repo.get_by_id(
            subscription_id
        )
        if subscription is None:
            raise NotFoundException(
                "Subscription",
                str(subscription_id),
            )
        update_data = data.model_dump(
            exclude_unset=True
        )
        update_data["updated_by"] = user_id
        updated = await self.subscription_repo.update(
            subscription_id,
            **update_data,
        )
        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="update_subscription",
            resource_type="subscription",
            resource_id=subscription_id,
            changes=update_data,
        )
        return SubscriptionResponse.model_validate(
            updated
        )