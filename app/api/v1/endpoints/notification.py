from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationCreate,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)

# Create Notification
@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    payload: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_notification(
        user_id=payload.user_id,
        title=payload.title,
        message=payload.message,
        notification_type=payload.notification_type,
        priority=payload.priority,
        data=payload.payload,
    )

# My Notifications
@router.get("")
async def my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.get_notifications(
        current_user.id,
        skip,
        limit,
    )

# Unread Notifications
@router.get("/unread")
async def unread_notifications(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.unread_notifications(
        current_user.id,
    )

# Notification Count
@router.get("/count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    unread = await service.unread_count(
        current_user.id,
    )

    notifications = await service.get_notifications(
        current_user.id,
        0,
        100000,
    )

    return {
        "total_notifications": len(notifications),
        "unread_notifications": unread,
        "read_notifications": len(notifications) - unread,
    }

# Mark Read
@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.mark_as_read(
        notification_id,
    )

# Mark All Read
@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.mark_all_read(
        current_user.id,
    )

# Delete Notification
@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.delete(
        notification_id,
    )

# Subscription Alert
@router.post("/alerts/subscription")
async def subscription_alert(
    hospital_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_subscription_expiry_alert(
        current_user.id,
        hospital_name,
    )

# Storage Alert
@router.post("/alerts/storage")
async def storage_alert(
    percentage: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_storage_alert(
        current_user.id,
        percentage,
    )

# Revenue Alert
@router.post("/alerts/revenue")
async def revenue_alert(
    revenue: float,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_revenue_alert(
        current_user.id,
        revenue,
    )

# Hospital Offline Alert
@router.post("/alerts/hospital-offline")
async def hospital_offline_alert(
    hospital_name: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_hospital_offline_alert(
        current_user.id,
        hospital_name,
    )

# Security Alert
@router.post("/alerts/security")
async def security_alert(
    message: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = NotificationService(db)

    return await service.create_security_alert(
        current_user.id,
        message,
    )