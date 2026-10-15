from pydantic import BaseModel, ConfigDict, Field
from beanie import PydanticObjectId


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: PydanticObjectId | None = None
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    name: str
    slug: str
    parent_id: PydanticObjectId | None
    description: str | None
    is_active: bool


class CategoryUpdate(BaseModel):
    name: str | None = Field(min_length=1, max_length=100, default=None)
    parent_id: PydanticObjectId | None = None
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True
