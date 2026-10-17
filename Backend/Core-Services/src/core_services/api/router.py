from fastapi import APIRouter

from core_services.api import (
    auth,
    user,
    category,
    product,
    inventory,
    wishlist,
    cart,
    checkout,
    orders,
    payments,
    admin_orders,
    vendor_orders,
    coupons,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(category.router)
api_router.include_router(product.router)
api_router.include_router(inventory.router)
api_router.include_router(wishlist.router)
api_router.include_router(cart.router)
api_router.include_router(checkout.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(admin_orders.router)
api_router.include_router(vendor_orders.router)
api_router.include_router(coupons.router)
