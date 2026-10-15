from slugify import slugify

from core_services.models.category import Category


async def generate_unique_slug(name: str) -> str:
    base = slugify(name) or "category"
    slug = base
    counter = 2
    while await Category.find_one(Category.slug == slug):
        slug = f"{base}-{counter}"
        counter += 1
    return slug
