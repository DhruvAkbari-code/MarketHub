from fastapi import APIRouter, Depends, status, HTTPException
from beanie import PydanticObjectId

from core_services.dependencies import require_roles
from core_services.models.user import Role, User
from core_services.models.category import Category
from core_services.schemas.category_schema import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from core_services.services.category_service import generate_unique_slug

router = APIRouter(prefix="/admin/categories", tags=["Admin"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin))],
)
async def create_category(payload: CategoryCreate):
    if await Category.find_one(Category.name == payload.name):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "The Categroy is Already Registered."
        )
    category = Category(
        **payload.model_dump(), slug=await generate_unique_slug(payload.name)
    )
    await category.insert()
    return category


@router.patch(
    "/{id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin))],
)
async def update_category(id: PydanticObjectId, payload: CategoryUpdate):
    category = await Category.get(id)
    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The Categroy not found.")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data and data["name"] != category.name:
        if await Category.find_one(Category.name == data["name"]):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "The Categroy is already registered."
            )
        data["slug"] = await generate_unique_slug(data["name"])

    await category.set(data)
    return category


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(Role.admin))],
)
async def delete_category(id: PydanticObjectId):
    category = await Category.get(id)
    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The Category not found.")
    await category.delete()


@router.get("", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK)
async def get_categories():
    return await Category.find_all().to_list()


@router.get(
    "/{slug}", response_model=list[CategoryResponse], status_code=status.HTTP_200_OK
)
async def get_categories_by_slug(slug: str):
    parent = await Category.find_one(Category.slug == slug)
    if not parent:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The category not found.")
    return await Category.find(Category.parent_id == parent.id).to_list()
