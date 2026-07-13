from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import BaseModel, AuditMixin


class Notification(BaseModel, AuditMixin):

    __tablename__ = "notifications"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    notification_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    priority = Column(
        String(20),
        default="MEDIUM",
    )

    payload = Column(
        JSON,
        default=dict,
    )

    is_read = Column(
        Boolean,
        default=False,
    )

    read_at = Column(
        DateTime,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    def __repr__(self):
        return (
            f"<Notification("
            f"{self.title}, "
            f"{self.user_id})>"
        )