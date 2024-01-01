import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import ChangeStatusError
from app.domain.carts.value_objects import CartStatusEnum


@pytest.mark.parametrize("cart_config", [{"min_cost_for_checkout": 0}], indirect=True)
async def test_ok(cart: Cart, cart_config: CartConfig) -> None:
    cart.lock()
    cart.complete()

    assert cart.status == CartStatusEnum.COMPLETED


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if CartStatusEnum.COMPLETED not in Cart.STATUS_TRANSITION_RULESET[status]
    ],
    indirect=True,
)
async def test_invalid_cart_status(cart: Cart) -> None:
    with pytest.raises(ChangeStatusError, match=""):
        cart.complete()
