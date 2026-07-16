from datetime import date, datetime
from typing import Any
from sqlalchemy import Select

class FilterBuilder:

    """
    Generic SQLAlchemy filter helper.
    """

    @staticmethod
    def apply_filters(
        query: Select,
        model,
        filters: dict[str, Any],
    ) -> Select:

        for field, value in filters.items():

            if value is None:
                continue

            if not hasattr(model, field):
                continue

            query = query.where(
                getattr(model, field) == value
            )

        return query

    # Date Range
    @staticmethod
    def date_range(
        query: Select,
        model,
        field_name: str,
        from_date: date | datetime | None = None,
        to_date: date | datetime | None = None,
    ) -> Select:

        column = getattr(model, field_name)

        if from_date:
            query = query.where(column >= from_date)

        if to_date:
            query = query.where(column <= to_date)

        return query

    # Boolean Filter
    @staticmethod
    def boolean(
        query: Select,
        model,
        field_name: str,
        value: bool | None,
    ) -> Select:

        if value is None:
            return query

        return query.where(
            getattr(model, field_name) == value
        )

    # IN Filter
    @staticmethod
    def in_filter(
        query: Select,
        model,
        field_name: str,
        values: list | None,
    ) -> Select:

        if not values:
            return query

        return query.where(
            getattr(model, field_name).in_(values)
        )

    # Like Filter
    @staticmethod
    def like(
        query: Select,
        model,
        field_name: str,
        keyword: str | None,
    ) -> Select:

        if not keyword:
            return query

        return query.where(
            getattr(model, field_name).ilike(
                f"%{keyword}%"
            )
        )

    # Starts With
    @staticmethod
    def starts_with(
        query: Select,
        model,
        field_name: str,
        keyword: str | None,
    ) -> Select:

        if not keyword:
            return query

        return query.where(
            getattr(model, field_name).ilike(
                f"{keyword}%"
            )
        )

    # Ends With
    @staticmethod
    def ends_with(
        query: Select,
        model,
        field_name: str,
        keyword: str | None,
    ) -> Select:

        if not keyword:
            return query

        return query.where(
            getattr(model, field_name).ilike(
                f"%{keyword}"
            )
        )

    # Between Numbers
    @staticmethod
    def between(
        query: Select,
        model,
        field_name: str,
        minimum=None,
        maximum=None,
    ) -> Select:

        column = getattr(model, field_name)

        if minimum is not None:
            query = query.where(column >= minimum)

        if maximum is not None:
            query = query.where(column <= maximum)

        return query

    # Multiple Filters
    @staticmethod
    def corporate_dashboard_filters(
        query: Select,
        model,
        *,
        hospital_group_id=None,
        hospital_id=None,
        status=None,
        city=None,
        state=None,
        from_date=None,
        to_date=None,
    ):

        query = FilterBuilder.apply_filters(
            query,
            model,
            {
                "hospital_group_id": hospital_group_id,
                "hospital_id": hospital_id,
                "status": status,
                "city": city,
                "state": state,
            },
        )

        query = FilterBuilder.date_range(
            query,
            model,
            "created_at",
            from_date,
            to_date,
        )

        return query