from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cart_coupons.entities import CartCoupon
from app.domain.interfaces.repositories.cart_coupons.repo import ICartCouponsRepository
from app.infra.repositories.sqla import models


class CartCouponsRepository(ICartCouponsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, cart_coupon: CartCoupon) -> CartCoupon:
        stmt = insert(models.CartCoupon).values(
            cart_id=cart_coupon.cart.id,
            coupon_id=cart_coupon.coupon_id,
            min_cart_cost=cart_coupon.min_cart_cost,
            discount_abs=cart_coupon.discount_abs,
        )
        await self._session.execute(stmt)

        return cart_coupon

    async def delete(self, cart_id: UUID) -> None:
        stmt = delete(models.CartCoupon).where(models.CartCoupon.cart_id == cart_id)
        await self._session.execute(stmt)
