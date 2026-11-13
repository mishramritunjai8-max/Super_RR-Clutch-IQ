"""
SUPER RR — CLUTCH IQ
FastAPI Dependencies & Pagination Utility
"""

from typing import List, Tuple, TypeVar
from backend.api.services.data_service import DataService
from backend.api.schemas.common import PaginationMetadata

T = TypeVar("T")


def get_data_service() -> DataService:
    """Dependency provider for DataService singleton."""
    return DataService.get_instance()


def paginate(items: List[T], page: int, page_size: int) -> Tuple[List[T], PaginationMetadata]:
    """Slices an in-memory list and builds standard PaginationMetadata."""
    total_records = len(items)
    pagination = PaginationMetadata.create(page=page, page_size=page_size, total_records=total_records)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = items[start_idx:end_idx]
    
    return page_items, pagination
