from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.carts.value_objects import CartStatusEnum


class ItemOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    id: int
    name: str
    qty: Decimal
    price: Decimal
    cost: Decimal
    is_weight: bool


class CartCouponOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    coupon_id: str
    min_cart_cost: Decimal
    discount_abs: Decimal
    cart_cost: Decimal
    applied: bool


class CartOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    id: UUID
    user_id: int
    status: CartStatusEnum
    items: list[ItemOutputDTO]
    items_qty: Decimal
    cost: Decimal
    checkout_enabled: bool
    coupon: CartCouponOutputDTO | None = None


class CartApplyCouponInputDTO(BaseModel):
    cart_id: UUID
    coupon_name: str
    auth_data: str


class CartRemoveCouponInputDTO(BaseModel):
    cart_id: UUID
    auth_data: str
