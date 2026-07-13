from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
from ..models.subscription import Subscription, SubscriptionPlan
from ..core.exceptions import DuplicateResourceException, BusinessRuleException
from .base import BaseRepository


class SubscriptionPlanRepository(BaseRepository):
    """Subscription plan repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, SubscriptionPlan)
    
    def get_by_code(self, code: str) -> Optional[SubscriptionPlan]:
        """Get plan by code."""
        return self.db.query(SubscriptionPlan).filter(SubscriptionPlan.code == code).first()
    
    def get_active_plans(self) -> List[SubscriptionPlan]:
        """Get all active plans."""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).all()


class SubscriptionRepository(BaseRepository):
    """Subscription repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, Subscription)
    
    def get_by_hospital(self, hospital_id: UUID) -> Optional[Subscription]:
        """Get subscription by hospital."""
        return self.db.query(Subscription).filter(
            Subscription.hospital_id == hospital_id,
            Subscription.is_active == True
        ).first()
    
    def get_active_subscriptions(self) -> List[Subscription]:
        """Get all active subscriptions."""
        now = datetime.utcnow()
        return self.db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.status == "active",
            Subscription.end_date >= now
        ).all()
    
    def get_expiring_subscriptions(self, days: int = 30) -> List[Subscription]:
        """Get subscriptions expiring within days."""
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=days)
        return self.db.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.status == "active",
            Subscription.end_date.between(now, expiry_date)
        ).all()
    
    def create_subscription(self, data: dict) -> Subscription:
        """Create subscription with validation."""
        # Check if hospital already has a subscription
        existing = self.get_by_hospital(data.get("hospital_id"))
        if existing:
            raise BusinessRuleException("Hospital already has an active subscription")
        
        return self.create(**data)