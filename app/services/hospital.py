from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from ..repositories.hospital import HospitalRepository
from ..repositories.audit import AuditRepository
from ..schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from ..core.exceptions import NotFoundException, BusinessRuleException
from ..core.logging import create_audit_log
import logging

logger = logging.getLogger(__name__)


class HospitalService:
    """Hospital service with business logic."""
    
    def __init__(self, db: Session):
        self.hospital_repo = HospitalRepository(db)
        self.audit_repo = AuditRepository(db)
        self.db = db
    
    def create_hospital(self, data: HospitalCreate, user_id: UUID) -> HospitalResponse:
        """Create a new hospital."""
        logger.info(f"Creating hospital: {data.name}")
        
        # Additional business validations
        if len(data.code) < 2:
            raise BusinessRuleException("Hospital code must be at least 2 characters")
        
        # Create hospital
        hospital_data = data.model_dump()
        hospital_data["created_by"] = user_id
        hospital = self.hospital_repo.create_hospital(hospital_data)
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="create_hospital",
            resource_type="hospital",
            resource_id=hospital.id,
            resource_data={"name": hospital.name, "code": hospital.code}
        )
        
        return HospitalResponse.model_validate(hospital)
    
    def get_hospital(self, hospital_id: UUID) -> HospitalResponse:
        """Get hospital by ID."""
        hospital = self.hospital_repo.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital", str(hospital_id))
        return HospitalResponse.model_validate(hospital)
    
    def get_hospitals(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[List[HospitalResponse], int]:
        """Get list of hospitals with pagination."""
        if search:
            hospitals = self.hospital_repo.search_hospitals(search)
            total = len(hospitals)
        else:
            hospitals = self.hospital_repo.get_all(skip=skip, limit=limit, is_deleted=False)
            total = self.hospital_repo.get_count(is_deleted=False)
        
        return [HospitalResponse.model_validate(h) for h in hospitals], total
    
    def update_hospital(self, hospital_id: UUID, data: HospitalUpdate, user_id: UUID) -> HospitalResponse:
        """Update hospital."""
        logger.info(f"Updating hospital: {hospital_id}")
        
        hospital = self.hospital_repo.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital", str(hospital_id))
        
        # Track changes for audit
        old_data = {col.name: getattr(hospital, col.name) for col in hospital.__table__.columns}
        
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        updated_hospital = self.hospital_repo.update(hospital_id, **update_data)
        
        # Create audit log
        changes = {k: v for k, v in update_data.items() if k in old_data and old_data.get(k) != v}
        if changes:
            create_audit_log(
                db=self.db,
                user_id=user_id,
                action="update_hospital",
                resource_type="hospital",
                resource_id=hospital_id,
                changes=changes,
                resource_data={"name": updated_hospital.name}
            )
        
        return HospitalResponse.model_validate(updated_hospital)
    
    def deactivate_hospital(self, hospital_id: UUID, user_id: UUID) -> bool:
        """Deactivate hospital (soft delete)."""
        logger.info(f"Deactivating hospital: {hospital_id}")
        
        hospital = self.hospital_repo.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital", str(hospital_id))
        
        if not hospital.is_active:
            raise BusinessRuleException("Hospital is already deactivated")
        
        # Soft delete hospital
        self.hospital_repo.delete(hospital_id)
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="deactivate_hospital",
            resource_type="hospital",
            resource_id=hospital_id,
            resource_data={"name": hospital.name, "code": hospital.code}
        )
        
        return True
    
    def activate_hospital(self, hospital_id: UUID, user_id: UUID) -> HospitalResponse:
        """Activate hospital."""
        logger.info(f"Activating hospital: {hospital_id}")
        
        hospital = self.hospital_repo.get_by_id(hospital_id)
        if not hospital:
            raise NotFoundException("Hospital", str(hospital_id))
        
        if hospital.is_active:
            raise BusinessRuleException("Hospital is already active")
        
        updated_hospital = self.hospital_repo.update(hospital_id, is_active=True, updated_by=user_id)
        
        # Create audit log
        create_audit_log(
            db=self.db,
            user_id=user_id,
            action="activate_hospital",
            resource_type="hospital",
            resource_id=hospital_id,
            resource_data={"name": hospital.name}
        )
        
        return HospitalResponse.model_validate(updated_hospital)
    
    def get_hospital_with_subscription(self, hospital_id: UUID) -> Optional[dict]:
        """Get hospital with subscription details."""
        hospital = self.hospital_repo.get_with_subscription(hospital_id)
        if not hospital:
            return None
        
        result = HospitalResponse.model_validate(hospital).model_dump()
        if hasattr(hospital, 'subscription') and hospital.subscription:
            result['subscription'] = {
                'plan': hospital.subscription.plan.name if hospital.subscription.plan else None,
                'start_date': hospital.subscription.start_date,
                'end_date': hospital.subscription.end_date,
                'status': hospital.subscription.status
            }
        
        return result