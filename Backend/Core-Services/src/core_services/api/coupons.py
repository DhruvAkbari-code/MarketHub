from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core_services.dependencies import get_db, require_roles
from core_services.models.order import Coupon
from core_services.models.user import Role, User
from core_services.schemas.order_schema import CouponCreate, CouponResponse

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    payload: CouponCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_roles(Role.admin)),
) -> Coupon:
    coupon = Coupon(
        code=payload.code.strip().upper(),
        discount_percent=payload.discount_percent,
    )
    db.add(coupon)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Coupon code already exists.",
        ) from exc
    await db.refresh(coupon)
    return coupon


@router.get("", response_model=list[CouponResponse])
async def list_coupons(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_roles(Role.admin)),
) -> list[Coupon]:
    result = await db.exec(select(Coupon).order_by(Coupon.code))
    return list(result.all())


@router.patch("/{coupon_id}/deactivate", response_model=CouponResponse)
async def deactivate_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_roles(Role.admin)),
) -> Coupon:
    coupon = await db.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found."
        )
    coupon.is_active = False
    await db.commit()
    await db.refresh(coupon)
    return coupon
