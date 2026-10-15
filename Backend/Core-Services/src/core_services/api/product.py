from uuid import UUID
from datetime import datetime, timezone
from beanie import PydanticObjectId
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    Depends,
    status,
)

from core_services.models.category import Category
from core_services.models.product import Product, ProductImage, ProductVariant
from core_services.models.user import User, Role
from core_services.dependencies import require_roles
from core_services.schemas.product_schema import (
    ImageReorder,
    ImageUpdate,
    ProductCreate,
    ProductImageResponse,
    ProductResponse,
    ProductUpdate,
)
from core_services.services.product_service import delete_image, upload_image

router = APIRouter(prefix="/products", tags=["products"])


async def get_owned_product(id: PydanticObjectId, vendor: User) -> Product:
    product = await Product.get(id)

    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The product not found.")
    if product.vendor_id != vendor.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not own this product.")
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate, vendor: User = Depends(require_roles(Role.vendor))
):
    category = await Category.get(payload.category_id)
    if not category or not category.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "the category not found.")

    product = Product(
        vendor_id=vendor.id,
        category_id=payload.category_id,
        name=payload.name.strip(),
        description=payload.description,
        variants=[ProductVariant(**v.model_dump()) for v in payload.variants],
    )
    await product.insert()
    return product


@router.get("", response_model=list[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)
):
    return (
        await Product.find(Product.is_active == True).skip(skip).limit(limit).to_list()
    )


@router.get("/search", response_model=list[ProductResponse])
async def search_products(
    q: str = Query(min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return (
        await Product.find({"$text": {"$search": q}, "is_active": True})
        .skip(skip)
        .limit(limit)
        .to_list()
    )


@router.get("/me", response_model=list[ProductResponse])
async def my_products(
    vendor: User = Depends(require_roles(Role.vendor)),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return (
        await Product.find(Product.vendor_id == vendor.id)
        .skip(skip)
        .limit(limit)
        .to_list()
    )


@router.get("/vendor/{vendor_id}", response_model=list[ProductResponse])
async def products_by_vendor(
    vendor_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return (
        await Product.find(
            Product.vendor_id == vendor_id,
            Product.is_active == True,
        )
        .skip(skip)
        .limit(limit)
        .to_list()
    )


@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: PydanticObjectId):
    product = await Product.get(id)
    if not product or not product.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The product not found.")
    return product


@router.patch("/{id}", response_model=ProductResponse)
async def update_product(
    id: PydanticObjectId,
    payload: ProductUpdate,
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await get_owned_product(id, vendor)
    data = payload.model_dump(exclude_unset=True)

    if "category_id" in data:
        category = await Category.get(data["category_id"])
        if not category or not category.is_active:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "The category not found.")
    if "name" in data:
        data["name"] = data["name"].strip()

    data["updated_at"] = datetime.now(timezone.utc)
    await product.set(data)
    return product


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: PydanticObjectId, vendor: User = Depends(require_roles(Role.vendor))
):
    product = await get_owned_product(id, vendor)
    await product.set({"is_active": False, "updated_at": datetime.now(timezone.utc)})


@router.post(
    "/{id}/images",
    response_model=list[ProductImageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_image(
    id: PydanticObjectId,
    file: UploadFile = File(...),
    alt: str | None = Form(default=None, max_length=200),
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await get_owned_product(id, vendor)
    if len(product.images) >= 10:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "A product can have at most 10 images."
        )

    uploaded = await upload_image(file)
    product.images.append(ProductImage(**uploaded, alt=alt, order=len(product.images)))
    product.updated_at = datetime.now(timezone.utc)
    await product.save()
    return product.images


@router.patch("/{id}/images/reorder", response_model=list[ProductImageResponse])
async def reorder_images(
    id: PydanticObjectId,
    payload: ImageReorder,
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await get_owned_product(id, vendor)
    current = {img.id: img for img in product.images}
    if set(payload.image_ids) != set(current) or len(payload.image_ids) != len(current):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Send every image id of this product exactly once.",
        )

    product.images = [current[i] for i in payload.image_ids]
    for position, img in enumerate(product.images):
        img.order = position
    product.updated_at = datetime.now(timezone.utc)
    await product.save()
    return product.images


@router.patch("/{id}/images/{image_id}", response_model=ProductImageResponse)
async def update_image(
    id: PydanticObjectId,
    image_id: UUID,
    payload: ImageUpdate,
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await get_owned_product(id, vendor)
    image = next((i for i in product.images if i.id == image_id), None)
    if not image:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The image not found.")

    image.alt = payload.alt
    product.updated_at = datetime.now(timezone.utc)
    await product.save()
    return image


@router.delete("/{id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    id: PydanticObjectId,
    image_id: UUID,
    vendor: User = Depends(require_roles(Role.vendor)),
):
    product = await get_owned_product(id, vendor)
    image = next((i for i in product.images if i.id == image_id), None)
    if not image:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "The image not found.")

    product.images = [i for i in product.images if i.id != image_id]
    for position, img in enumerate(product.images):
        img.order = position
    product.updated_at = datetime.now(timezone.utc)
    await product.save()
    await delete_image(image.public_id)
