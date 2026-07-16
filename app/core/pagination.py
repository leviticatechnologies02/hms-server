from math import ceil
from typing import Any


class Pagination:

    @staticmethod
    def paginate(
        *,
        items: list[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ):

        if page <= 0:
            page = 1

        if page_size <= 0:
            page_size = 20

        total_pages = ceil(total / page_size) if total else 1

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None,
            "results": items,
        }


class PaginationParams:

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
    ):

        self.page = page
        self.page_size = page_size

    @property
    def offset(self):

        return (self.page - 1) * self.page_size

    @property
    def limit(self):

        return self.page_size