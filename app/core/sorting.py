from sqlalchemy import Select, asc, desc

class SortBuilder:
    """
    Generic SQLAlchemy Sorting Helper
    """

    @staticmethod
    def apply_sort(
        query: Select,
        model,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> Select:

        if not hasattr(model, sort_by):
            sort_by = "created_at"

        column = getattr(model, sort_by)

        if order.lower() == "asc":
            return query.order_by(asc(column))

        return query.order_by(desc(column))

    # Hospital Sorting
    @staticmethod
    def hospital_sort(
        query: Select,
        model,
        sort_by: str = "name",
        order: str = "asc",
    ):

        allowed = [
            "name",
            "city",
            "state",
            "created_at",
            "updated_at",
        ]

        if sort_by not in allowed:
            sort_by = "name"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )

    # Corporate Sorting
    @staticmethod
    def corporate_sort(
        query: Select,
        model,
        sort_by: str = "created_at",
        order: str = "desc",
    ):

        allowed = [
            "name",
            "code",
            "created_at",
            "updated_at",
            "max_users",
            "max_hospitals",
            "current_storage_gb",
        ]

        if sort_by not in allowed:
            sort_by = "created_at"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )

    # Hospital Group Sorting
    @staticmethod
    def hospital_group_sort(
        query: Select,
        model,
        sort_by: str = "name",
        order: str = "asc",
    ):

        allowed = [
            "name",
            "code",
            "city",
            "created_at",
            "total_hospitals",
            "total_branches",
            "total_patients",
        ]

        if sort_by not in allowed:
            sort_by = "name"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )

    # Report Sorting
    @staticmethod
    def report_sort(
        query: Select,
        model,
        sort_by: str = "created_at",
        order: str = "desc",
    ):

        allowed = [
            "title",
            "report_type",
            "status",
            "created_at",
            "updated_at",
            "download_count",
            "file_size",
        ]

        if sort_by not in allowed:
            sort_by = "created_at"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )

    # Notification Sorting
    @staticmethod
    def notification_sort(
        query: Select,
        model,
        sort_by: str = "created_at",
        order: str = "desc",
    ):

        allowed = [
            "created_at",
            "priority",
            "notification_type",
            "is_read",
        ]

        if sort_by not in allowed:
            sort_by = "created_at"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )

    # KPI Sorting
    @staticmethod
    def branch_kpi_sort(
        query: Select,
        model,
        sort_by: str = "report_date",
        order: str = "desc",
    ):

        allowed = [
            "report_date",
            "total_revenue",
            "net_profit",
            "total_patients",
            "total_doctors",
            "patient_satisfaction",
            "bed_occupancy_percentage",
        ]

        if sort_by not in allowed:
            sort_by = "report_date"

        return SortBuilder.apply_sort(
            query,
            model,
            sort_by,
            order,
        )