from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from ..repositories.subscription import SubscriptionRepository, SubscriptionPlanRepository
from ..repositories.hospital import HospitalRepository
from ..schemas.subscription import (
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
)
from ..core.exceptions import NotFoundException, BusinessRuleException
from ..core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Subscription service with business logic."""
    
    def __init__(self, db: Session):
        self.subscription_repo = SubscriptionRepository(db)
        self.plan_repo = SubscriptionPlanRepository(db)
        self.hospital_repo = HospitalRepository(db)
        self.db = db
    
    def create_plan(self, data: SubscriptionPlanCreate, user_id: UUID) -> SubscriptionPlanResponse:
        """Create a subscription plan."""
        logger.info(f"Creating subscription plan: {data.name}")
        
        # Check for duplicate code
        existing = self.plan_repo.get_by_code(data.code)
        if existing:
            raise BusinessRuleException(f"Plan with code '{data.code}' already exists")
        
        plan_data = data.model_dump()
        plan_data["created_by"] = user_id
        plan = self.plan_repo.create(**plan_data)
        
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="create_subscription_plan",
            resource_type="subscription_plan",
            resource_id=plan.id,
            resource_data={"name": plan.name, "code": plan.code}
        )
        
        return SubscriptionPlanResponse.model_validate(plan)
    
    def get_plans(self) -> List[SubscriptionPlanResponse]:
        """Get all subscription plans."""
        plans = self.plan_repo.get_active_plans()
        return [SubscriptionPlanResponse.model_validate(p) for p in plans]
    
    def assign_subscription(self, data: SubscriptionCreate, user_id: UUID) -> SubscriptionResponse:
        """Assign subscription to a hospital."""
        logger.info(f"Assigning subscription to hospital: {data.hospital_id}")
        
        # Validate hospital exists
        hospital = self.hospital_repo.get_by_id(data.hospital_id)
        if not hospital:
            raise NotFoundException("Hospital", str(data.hospital_id))
        
        # Validate plan exists
        plan = self.plan_repo.get_by_id(data.plan_id)
        if not plan:
            raise NotFoundException("Plan", str(data.plan_id))
        
        # Check if hospital already has subscription
        existing = self.subscription_repo.get_by_hospital(data.hospital_id)
        if existing:
            raise BusinessRuleException("Hospital already has an active subscription")
        
        subscription_data = data.model_dump()
        subscription_data["created_by"] = user_id
        subscription = self.subscription_repo.create_subscription(subscription_data)
        
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="assign_subscription",
            resource_type="subscription",
            resource_id=subscription.id,
            resource_data={
                "hospital_id": str(data.hospital_id),
                "plan_id": str(data.plan_id)
            }
        )
        
        return SubscriptionResponse.model_validate(subscription)
    
    def get_hospital_subscription(self, hospital_id: UUID) -> Optional[SubscriptionResponse]:
        """Get subscription for a hospital."""
        subscription = self.subscription_repo.get_by_hospital(hospital_id)
        if not subscription:
            return None
        return SubscriptionResponse.model_validate(subscription)
    
    def get_expiring_subscriptions(self, days: int = 30) -> List[SubscriptionResponse]:
        """Get subscriptions expiring soon."""
        subscriptions = self.subscription_repo.get_expiring_subscriptions(days)
        return [SubscriptionResponse.model_validate(s) for s in subscriptions]
    
    def update_subscription(self, subscription_id: UUID, data: SubscriptionUpdate, user_id: UUID) -> SubscriptionResponse:
        """Update subscription."""
        subscription = self.subscription_repo.get_by_id(subscription_id)
        if not subscription:
            raise NotFoundException("Subscription", str(subscription_id))
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        updated_subscription = self.subscription_repo.update(subscription_id, **update_data)
        
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="update_subscription",
            resource_type="subscription",
            resource_id=subscription_id,
            changes=update_data
        )
        
        return SubscriptionResponse.model_validate(updated_subscription)