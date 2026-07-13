from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from ....core.database import get_db
from ....core.dependencies import get_current_super_admin
from ....models.user import User
from ....schemas.subscription import (
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
)
from ....schemas.common import ResponseModel
from ....services.subscription import SubscriptionService
from ....services.hospital import HospitalService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Super Admin - Subscriptions"])


@router.post(
    "/plans",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create Subscription Plan",
    description="Create a new subscription plan"
)
async def create_plan(
    data: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Create a new subscription plan."""
    service = SubscriptionService(db)
    plan = service.create_plan(data, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Subscription plan created successfully",
        data=plan.model_dump()
    )


@router.get(
    "/plans",
    response_model=ResponseModel,
    summary="List Subscription Plans",
    description="Get all subscription plans"
)
async def list_plans(
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """List all subscription plans."""
    service = SubscriptionService(db)
    plans = service.get_plans()
    
    return ResponseModel(
        success=True,
        message="Subscription plans retrieved successfully",
        data=[plan.model_dump() for plan in plans]
    )


@router.post(
    "/assign",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Subscription",
    description="Assign a subscription plan to a hospital"
)
async def assign_subscription(
    data: SubscriptionCreate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Assign subscription to hospital."""
    service = SubscriptionService(db)
    subscription = service.assign_subscription(data, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Subscription assigned successfully",
        data=subscription.model_dump()
    )


@router.get(
    "/hospital/{hospital_id}",
    response_model=ResponseModel,
    summary="Get Hospital Subscription",
    description="Get subscription for a specific hospital"
)
async def get_hospital_subscription(
    hospital_id: UUID,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get hospital subscription."""
    service = SubscriptionService(db)
    subscription = service.get_hospital_subscription(hospital_id)
    
    if not subscription:
        return ResponseModel(
            success=False,
            message="No subscription found for this hospital",
            data=None
        )
    
    return ResponseModel(
        success=True,
        message="Subscription retrieved successfully",
        data=subscription.model_dump()
    )


@router.get(
    "/expiring",
    response_model=ResponseModel,
    summary="Get Expiring Subscriptions",
    description="Get subscriptions expiring within specified days"
)
async def get_expiring_subscriptions(
    days: int = Query(30, ge=1, le=365, description="Days to check for expiry"),
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Get expiring subscriptions."""
    service = SubscriptionService(db)
    subscriptions = service.get_expiring_subscriptions(days)
    
    return ResponseModel(
        success=True,
        message=f"Found {len(subscriptions)} subscriptions expiring within {days} days",
        data=[sub.model_dump() for sub in subscriptions]
    )


@router.put(
    "/{subscription_id}",
    response_model=ResponseModel,
    summary="Update Subscription",
    description="Update subscription details"
)
async def update_subscription(
    subscription_id: UUID,
    data: SubscriptionUpdate,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Update subscription."""
    service = SubscriptionService(db)
    subscription = service.update_subscription(subscription_id, data, current_user.id)
    
    return ResponseModel(
        success=True,
        message="Subscription updated successfully",
        data=subscription.model_dump()
    )