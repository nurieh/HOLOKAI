
from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, gt=0)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
