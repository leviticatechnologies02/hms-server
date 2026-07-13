from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from ..models.hospital import Hospital
from ..core.exceptions import DuplicateResourceException
from .base import BaseRepository


class HospitalRepository(BaseRepository):
    """Hospital repository."""
    
    def __init__(self, db: Session):
        super().__init__(db, Hospital)
    
    def get_by_code(self, code: str) -> Optional[Hospital]:
        """Get hospital by code."""
        return self.db.query(Hospital).filter(Hospital.code == code).first()
    
    def get_by_email(self, email: str) -> Optional[Hospital]:
        """Get hospital by email."""
        return self.db.query(Hospital).filter(Hospital.email == email).first()
    
    def get_with_subscription(self, hospital_id: UUID) -> Optional[Hospital]:
        """Get hospital with subscription."""
        return self.db.query(Hospital).filter(
            Hospital.id == hospital_id,
            Hospital.is_deleted == False
        ).first()
    
    def create_hospital(self, data: dict) -> Hospital:
        """Create hospital with validation."""
        # Check for duplicate code
        existing = self.get_by_code(data.get("code"))
        if existing:
            raise DuplicateResourceException("Hospital", "code", data.get("code"))
        
        # Check for duplicate email
        existing = self.get_by_email(data.get("email"))
        if existing:
            raise DuplicateResourceException("Hospital", "email", data.get("email"))
        
        return self.create(**data)
    
    def search_hospitals(self, query: str) -> List[Hospital]:
        """Search hospitals by name, code, or email."""
        return self.db.query(Hospital).filter(
            Hospital.is_deleted == False,
            (Hospital.name.ilike(f"%{query}%") |
             Hospital.code.ilike(f"%{query}%") |
             Hospital.email.ilike(f"%{query}%"))
        ).all()
    
    def get_active_hospitals(self) -> List[Hospital]:
        """Get all active hospitals."""
        return self.db.query(Hospital).filter(
            Hospital.is_active == True,
            Hospital.is_deleted == False
        ).all()