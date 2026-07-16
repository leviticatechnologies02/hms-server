from fastapi import APIRouter

from .endpoints.hospital import router as hospitals_router
from .endpoints.auth import router as auth_router
from .endpoints.subscriptions import router as subscriptions_router
from .endpoints.audit import router as audit_router
from .endpoints.roles import router as roles_router
from .endpoints.users import router as users_router
from .endpoints.corporate import router as corporate_router
from .endpoints.hospital_group import router as hospital_group_router
from .endpoints.branch_kpi import router as branch_kpi_router
from .endpoints.corporate_settings import router as corporate_settings_router
from .endpoints.notification import router as notification_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router, tags=["Authentication"])
router.include_router(hospitals_router, prefix="/super-admin", tags=["Super Admin - Hospitals"])
router.include_router(subscriptions_router, prefix="/super-admin", tags=["Super Admin - Subscriptions"])
router.include_router(audit_router, prefix="/super-admin", tags=["Super Admin - Audit Logs"])
router.include_router(roles_router, prefix="/super-admin", tags=["Super Admin - Roles & Permissions"])
router.include_router(users_router, prefix="/super-admin", tags=["Super Admin - Platform Users"])
router.include_router(corporate_router, prefix="/corporate", tags=["Corporate Admin"])
router.include_router(hospital_group_router, prefix="/corporate/groups", tags=["Corporate Hospital Groups"])
router.include_router(branch_kpi_router, prefix="/corporate/kpis", tags=["Corporate Branch KPI"])
