"""
SUPER RR — CLUTCH IQ
Common Pydantic Schemas & Pagination Models
"""

import math
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_records: int = Field(..., description="Total matching records across all pages")
    total_pages: int = Field(..., description="Total number of available pages")
    has_next: bool = Field(..., description="True if a subsequent page exists")
    has_prev: bool = Field(..., description="True if a previous page exists")

    @classmethod
    def create(cls, page: int, page_size: int, total_records: int) -> "PaginationMetadata":
        total_pages = max(1, math.ceil(total_records / page_size)) if total_records > 0 else 1
        return cls(
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items for the requested page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error description")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of error occurrence")
