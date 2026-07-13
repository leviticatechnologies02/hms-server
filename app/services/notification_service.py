# app/services/notification_service.py

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = NotificationRepository(db)

    # Create Notification
    async def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        priority: str = "MEDIUM",
        data: dict | None = None,
    ):

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            payload=data or {},
            created_at=datetime.utcnow(),
        )

        return await self.repository.create(notification)

    # User Notifications
    async def get_notifications(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        return await self.repository.get_user_notifications(
            user_id,
            skip,
            limit,
        )

    # Unread Notifications
    async def unread_notifications(
        self,
        user_id: UUID,
    ):

        return await self.repository.get_unread_notifications(
            user_id
        )

    # Notification Count
    async def unread_count(
        self,
        user_id: UUID,
    ):

        return await self.repository.unread_count(
            user_id
        )

    # Mark Read
    async def mark_as_read(
        self,
        notification_id: UUID,
    ):

        notification = await self.repository.get_by_id(
            notification_id
        )

        if not notification:
            raise ValueError(
                "Notification not found."
            )

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        return await self.repository.update(
            notification
        )

    # Mark All Read
    async def mark_all_read(
        self,
        user_id: UUID,
    ):

        notifications = (
            await self.repository.get_unread_notifications(
                user_id
            )
        )

        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()

            await self.repository.update(
                notification
            )

        return {
            "message": "All notifications marked as read."
        }

    # Delete Notification
    async def delete(
        self,
        notification_id: UUID,
    ):

        notification = await self.repository.get_by_id(
            notification_id
        )

        if not notification:
            raise ValueError(
                "Notification not found."
            )

        await self.repository.delete(notification)

        return {
            "message": "Notification deleted successfully."
        }

    # Corporate Alerts
    async def create_subscription_expiry_alert(
        self,
        user_id: UUID,
        hospital_name: str,
    ):

        return await self.create_notification(
            user_id=user_id,
            title="Subscription Expiry",
            message=f"{hospital_name} subscription will expire soon.",
            notification_type="SUBSCRIPTION",
            priority="HIGH",
        )

    async def create_storage_alert(
        self,
        user_id: UUID,
        percentage: int,
    ):

        return await self.create_notification(
            user_id=user_id,
            title="Storage Alert",
            message=f"Storage usage reached {percentage}%.",
            notification_type="STORAGE",
            priority="HIGH",
        )

    async def create_revenue_alert(
        self,
        user_id: UUID,
        revenue,
    ):

        return await self.create_notification(
            user_id=user_id,
            title="Revenue Target Achieved",
            message=f"Revenue reached ₹{revenue}.",
            notification_type="REVENUE",
            priority="MEDIUM",
        )

    async def create_hospital_offline_alert(
        self,
        user_id: UUID,
        hospital_name: str,
    ):

        return await self.create_notification(
            user_id=user_id,
            title="Hospital Offline",
            message=f"{hospital_name} is currently offline.",
            notification_type="SYSTEM",
            priority="CRITICAL",
        )

    async def create_security_alert(
        self,
        user_id: UUID,
        message: str,
    ):

        return await self.create_notification(
            user_id=user_id,
            title="Security Alert",
            message=message,
            notification_type="SECURITY",
            priority="CRITICAL",
        )