from uuid import UUID
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hospital import Hospital
from app.models.hospital_group import HospitalGroup
from app.models.corporate_account import CorporateAccount
from app.models.corporate_report import CorporateReport
from app.models.user import User


class SearchService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # Global Search
    async def global_search(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        hospitals = await self.search_hospitals(
            corporate_account_id,
            keyword,
        )

        groups = await self.search_groups(
            corporate_account_id,
            keyword,
        )

        reports = await self.search_reports(
            corporate_account_id,
            keyword,
        )

        users = await self.search_users(
            corporate_account_id,
            keyword,
        )

        return {
            "hospitals": hospitals,
            "groups": groups,
            "reports": reports,
            "users": users,
        }

    # Hospital Search
    async def search_hospitals(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        result = await self.db.execute(
            select(Hospital)
            .where(
                Hospital.corporate_account_id == corporate_account_id,
                Hospital.is_deleted == False,
                or_(
                    Hospital.name.ilike(f"%{keyword}%"),
                    Hospital.code.ilike(f"%{keyword}%"),
                    Hospital.city.ilike(f"%{keyword}%"),
                    Hospital.state.ilike(f"%{keyword}%"),
                ),
            )
            .order_by(Hospital.name)
        )

        return result.scalars().all()

    # Hospital Group Search
    async def search_groups(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        result = await self.db.execute(
            select(HospitalGroup)
            .where(
                HospitalGroup.corporate_account_id
                == corporate_account_id,
                HospitalGroup.is_deleted == False,
                or_(
                    HospitalGroup.name.ilike(f"%{keyword}%"),
                    HospitalGroup.code.ilike(f"%{keyword}%"),
                ),
            )
            .order_by(HospitalGroup.name)
        )

        return result.scalars().all()

    # Report Search
    async def search_reports(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        result = await self.db.execute(
            select(CorporateReport)
            .where(
                CorporateReport.corporate_account_id
                == corporate_account_id,
                CorporateReport.is_active == True,
                or_(
                    CorporateReport.title.ilike(f"%{keyword}%"),
                    CorporateReport.report_code.ilike(
                        f"%{keyword}%"
                    ),
                    CorporateReport.report_type.ilike(
                        f"%{keyword}%"
                    ),
                ),
            )
            .order_by(
                CorporateReport.created_at.desc()
            )
        )

        return result.scalars().all()

    # User Search
    async def search_users(
        self,
        corporate_account_id: UUID,
        keyword: str,
    ):

        result = await self.db.execute(
            select(User)
            .where(
                User.corporate_account_id
                == corporate_account_id,
                User.is_deleted == False,
                or_(
                    User.full_name.ilike(
                        f"%{keyword}%"
                    ),
                    User.email.ilike(
                        f"%{keyword}%"
                    ),
                    User.username.ilike(
                        f"%{keyword}%"
                    ),
                ),
            )
            .order_by(User.full_name)
        )

        return result.scalars().all()

    # Corporate Search
    async def search_corporates(
        self,
        keyword: str,
    ):

        result = await self.db.execute(
            select(CorporateAccount)
            .where(
                CorporateAccount.is_deleted == False,
                or_(
                    CorporateAccount.name.ilike(
                        f"%{keyword}%"
                    ),
                    CorporateAccount.code.ilike(
                        f"%{keyword}%"
                    ),
                    CorporateAccount.email.ilike(
                        f"%{keyword}%"
                    ),
                ),
            )
            .order_by(
                CorporateAccount.name
            )
        )

        return result.scalars().all()

    # Advanced Search
    async def advanced_search(
        self,
        corporate_account_id: UUID,
        keyword: str,
        search_type: str,
    ):

        if search_type == "hospital":
            return await self.search_hospitals(
                corporate_account_id,
                keyword,
            )

        if search_type == "group":
            return await self.search_groups(
                corporate_account_id,
                keyword,
            )

        if search_type == "report":
            return await self.search_reports(
                corporate_account_id,
                keyword,
            )

        if search_type == "user":
            return await self.search_users(
                corporate_account_id,
                keyword,
            )

        return await self.global_search(
            corporate_account_id,
            keyword,
        )