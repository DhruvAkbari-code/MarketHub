from fastapi import APIRouter

from core_services.api import auth, user, category, product, inventory, wishlist, cart

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(category.router)
api_router.include_router(product.router)
api_router.include_router(inventory.router)
api_router.include_router(wishlist.router)
api_router.include_router(cart.router)
