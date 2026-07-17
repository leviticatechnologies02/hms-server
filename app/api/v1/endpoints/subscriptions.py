from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....schemas.subscription import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionCreate,
    SubscriptionUpdate,
)
from ....schemas.common import ResponseModel
from ....services.subscription import SubscriptionService

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Super Admin - Subscriptions"]
)


@router.post(
    "/plans",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    data: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    plan = await service.create_plan(
        data,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Subscription plan created successfully",
        data=plan.model_dump(),
    )


@router.get(
    "/plans",
    response_model=ResponseModel,
)
async def list_plans(
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    plans = await service.get_plans()

    return ResponseModel(
        success=True,
        message="Subscription plans retrieved successfully",
        data=[plan.model_dump() for plan in plans],
    )


@router.post(
    "/assign",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def assign_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    subscription = await service.assign_subscription(
        data,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Subscription assigned successfully",
        data=subscription.model_dump(),
    )


@router.get(
    "/hospital/{hospital_id}",
    response_model=ResponseModel,
)
async def get_hospital_subscription(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    subscription = await service.get_hospital_subscription(
        hospital_id,
    )

    if subscription is None:
        return ResponseModel(
            success=False,
            message="No subscription found for this hospital",
            data=None,
        )

    return ResponseModel(
        success=True,
        message="Subscription retrieved successfully",
        data=subscription.model_dump(),
    )


@router.get(
    "/expiring",
    response_model=ResponseModel,
)
async def get_expiring_subscriptions(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    subscriptions = await service.get_expiring_subscriptions(
        days,
    )

    return ResponseModel(
        success=True,
        message=f"Found {len(subscriptions)} subscriptions expiring within {days} days",
        data=[sub.model_dump() for sub in subscriptions],
    )


@router.put(
    "/{subscription_id}",
    response_model=ResponseModel,
)
async def update_subscription(
    subscription_id: UUID,
    data: SubscriptionUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)

    subscription = await service.update_subscription(
        subscription_id,
        data,
        current_user.id,
    )

    return ResponseModel(
        success=True,
        message="Subscription updated successfully",
        data=subscription.model_dump(),
    )