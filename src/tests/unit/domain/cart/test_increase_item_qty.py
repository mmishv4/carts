from decimal import Decimal

import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import (
    CartItemDoesNotExistError,
    MaxItemsQtyLimitExceeded,
    OperationForbiddenError,
    SpecificItemQtyLimitExceeded,
)
from app.domain.carts.value_objects import CartStatusEnum


async def test_ok(cart: Cart, cart_item: CartItem) -> None:
    cart.add_new_item(cart_item)
    current_qty = cart_item.qty
    delta_qty = Decimal(10)
    cart.increase_item_qty(item_id=cart_item.id, qty=delta_qty)

    assert cart_item.qty == current_qty + delta_qty


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if status != CartStatusEnum.OPENED
    ],
    indirect=True,
)
async def test_cart_cant_be_modified(cart: Cart) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        cart.increase_item_qty(item_id=1, qty=Decimal(1))


async def test_item_doesnt_exist(cart: Cart, cart_config: CartConfig) -> None:
    with pytest.raises(CartItemDoesNotExistError, match=""):
        cart.increase_item_qty(item_id=1, qty=Decimal(1))


@pytest.mark.parametrize(
    ("cart_config", "cart_item"),
    [({"limit_items_by_id": {1: Decimal(0)}}, {"id": 1, "qty": Decimal(1)})],
    indirect=True,
)
async def test_item_qty_limit_exceeded(
    cart: Cart,
    cart_config: CartConfig,
    cart_item: CartItem,
) -> None:
    cart.items.append(cart_item)

    with pytest.raises(SpecificItemQtyLimitExceeded, match="limit: 0, actual: 2"):
        cart.increase_item_qty(item_id=1, qty=Decimal(1))


@pytest.mark.parametrize(
    ("cart_config", "cart_item"),
    [({"max_items_qty": Decimal(1)}, {"id": 1, "qty": Decimal(1), "is_weight": False})],
    indirect=True,
)
async def test_cart_items_qty_limit_exceeded(
    cart: Cart,
    cart_config: CartConfig,
    cart_item: CartItem,
) -> None:
    cart.items.append(cart_item)

    with pytest.raises(MaxItemsQtyLimitExceeded, match=""):
        cart.increase_item_qty(item_id=1, qty=Decimal(1))
