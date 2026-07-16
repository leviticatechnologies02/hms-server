from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import BusinessRuleException, NotFoundException
from ..core.logging import create_audit_log
from ..repositories.audit import AuditRepository
from ..repositories.hospital import HospitalRepository
from ..schemas.hospital import (
    HospitalCreate,
    HospitalResponse,
    HospitalUpdate,
)


class HospitalService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.hospital_repo = HospitalRepository(db)
        self.audit_repo = AuditRepository(db)

    # ==========================================================
    # Create
    # ==========================================================

    async def create_hospital(
        self,
        data: HospitalCreate,
        user_id: UUID,
    ):

        if len(data.code) < 2:
            raise BusinessRuleException(
                "Hospital code must be at least 2 characters."
            )

        hospital_data = data.model_dump()
        hospital_data["created_by"] = user_id

        hospital = await self.hospital_repo.create_hospital(
            hospital_data
        )

        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="create_hospital",
            resource_type="hospital",
            resource_id=hospital.id,
            resource_data={
                "name": hospital.name,
                "code": hospital.code,
            },
        )

        return HospitalResponse.model_validate(hospital)

    # ==========================================================
    # Get
    # ==========================================================

    async def get_hospital(
        self,
        hospital_id: UUID,
    ):

        hospital = await self.hospital_repo.get_by_id(
            hospital_id
        )

        if not hospital:
            raise NotFoundException(
                "Hospital",
                str(hospital_id),
            )

        return HospitalResponse.model_validate(hospital)

    # ==========================================================
    # List
    # ==========================================================

    async def get_hospitals(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ):

        if search:

            hospitals = await self.hospital_repo.search_hospitals(
                search
            )

            total = len(hospitals)

        else:

            hospitals = await self.hospital_repo.get_all(
                skip=skip,
                limit=limit,
                is_deleted=False,
            )

            total = await self.hospital_repo.get_count(
                is_deleted=False,
            )

        return (
            [
                HospitalResponse.model_validate(h)
                for h in hospitals
            ],
            total,
        )

    # ==========================================================
    # Update
    # ==========================================================

    async def update_hospital(
        self,
        hospital_id: UUID,
        data: HospitalUpdate,
        user_id: UUID,
    ):

        hospital = await self.hospital_repo.get_by_id(
            hospital_id
        )

        if not hospital:
            raise NotFoundException(
                "Hospital",
                str(hospital_id),
            )

        old_data = {
            column.name: getattr(hospital, column.name)
            for column in hospital.__table__.columns
        }

        update_data = data.model_dump(
            exclude_unset=True
        )

        update_data["updated_by"] = user_id

        updated = await self.hospital_repo.update(
            hospital_id,
            **update_data,
        )

        changes = {
            key: value
            for key, value in update_data.items()
            if old_data.get(key) != value
        }

        if changes:

            await create_audit_log(
                db=self.db,
                user_id=user_id,
                action="update_hospital",
                resource_type="hospital",
                resource_id=hospital_id,
                changes=changes,
                resource_data={
                    "name": updated.name,
                },
            )

        return HospitalResponse.model_validate(updated)

    # ==========================================================
    # Delete
    # ==========================================================

    async def deactivate_hospital(
        self,
        hospital_id: UUID,
        user_id: UUID,
    ):

        hospital = await self.hospital_repo.get_by_id(
            hospital_id
        )

        if not hospital:
            raise NotFoundException(
                "Hospital",
                str(hospital_id),
            )

        if not hospital.is_active:
            raise BusinessRuleException(
                "Hospital already deactivated."
            )

        await self.hospital_repo.delete(
            hospital_id
        )

        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="deactivate_hospital",
            resource_type="hospital",
            resource_id=hospital_id,
            resource_data={
                "name": hospital.name,
                "code": hospital.code,
            },
        )

        return True

    # ==========================================================
    # Activate
    # ==========================================================

    async def activate_hospital(
        self,
        hospital_id: UUID,
        user_id: UUID,
    ):

        hospital = await self.hospital_repo.get_by_id(
            hospital_id
        )

        if not hospital:
            raise NotFoundException(
                "Hospital",
                str(hospital_id),
            )

        if hospital.is_active:
            raise BusinessRuleException(
                "Hospital already active."
            )

        updated = await self.hospital_repo.update(
            hospital_id,
            is_active=True,
            updated_by=user_id,
        )

        await create_audit_log(
            db=self.db,
            user_id=user_id,
            action="activate_hospital",
            resource_type="hospital",
            resource_id=hospital_id,
            resource_data={
                "name": hospital.name,
            },
        )

        return HospitalResponse.model_validate(updated)

    # ==========================================================
    # Subscription
    # ==========================================================

    async def get_hospital_with_subscription(
        self,
        hospital_id: UUID,
    ):

        hospital = await self.hospital_repo.get_with_subscription(
            hospital_id
        )

        if not hospital:
            return None

        result = HospitalResponse.model_validate(
            hospital
        ).model_dump()

        if (
            hasattr(hospital, "subscription")
            and hospital.subscription
        ):

            result["subscription"] = {
                "plan": (
                    hospital.subscription.plan.name
                    if hospital.subscription.plan
                    else None
                ),
                "start_date": hospital.subscription.start_date,
                "end_date": hospital.subscription.end_date,
                "status": hospital.subscription.status,
            }

        return result