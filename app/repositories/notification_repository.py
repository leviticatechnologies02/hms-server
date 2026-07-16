from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Create
    async def create(
        self,
        notification: Notification,
    ) -> Notification:

        self.db.add(notification)

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    # Get By ID
    async def get_by_id(
        self,
        notification_id: UUID,
    ) -> Optional[Notification]:

        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.is_active == True,
            )
        )

        return result.scalar_one_or_none()

    # User Notifications
    async def get_user_notifications(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ):

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_active == True,
            )
            .order_by(
                Notification.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    # Unread Notifications
    async def get_unread_notifications(
        self,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_active == True,
                Notification.is_read == False,
            )
            .order_by(
                Notification.created_at.desc()
            )
        )

        return result.scalars().all()

    # Read Notifications
    async def get_read_notifications(
        self,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_active == True,
                Notification.is_read == True,
            )
            .order_by(
                Notification.created_at.desc()
            )
        )

        return result.scalars().all()

    # Unread Count
    async def unread_count(
        self,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(
                func.count(Notification.id)
            ).where(
                Notification.user_id == user_id,
                Notification.is_active == True,
                Notification.is_read == False,
            )
        )

        return result.scalar()

    # Update
    async def update(
        self,
        notification: Notification,
    ) -> Notification:

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    # Delete
    async def delete(
        self,
        notification: Notification,
    ):

        notification.is_active = False

        await self.db.commit()

    # Mark Read
    async def mark_read(
        self,
        notification: Notification,
    ):

        notification.is_read = True

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    # Mark Unread
    async def mark_unread(
        self,
        notification: Notification,
    ):

        notification.is_read = False

        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    # Delete All Notifications
    async def delete_all(
        self,
        user_id: UUID,
    ):

        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_active == True,
            )
        )

        notifications = result.scalars().all()

        for notification in notifications:
            notification.is_active = False

        await self.db.commit()

        return len(notifications)

    # Recent Notifications
    async def recent_notifications(
        self,
        user_id: UUID,
        limit: int = 10,
    ):

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_active == True,
            )
            .order_by(
                Notification.created_at.desc()
            )
            .limit(limit)
        )

        return result.scalars().all()

    # Notifications By Type
    async def get_by_type(
        self,
        user_id: UUID,
        notification_type: str,
    ):

        result = await self.db.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
                Notification.is_active == True,
            )
            .order_by(
                Notification.created_at.desc()
            )
        )

        return result.scalars().all()